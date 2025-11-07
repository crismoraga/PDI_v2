"""Detection with YOLOv12 and classification via SpeciesNet."""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import Any, List, Sequence, Union

import cv2
import numpy as np
import torch
from ultralytics import YOLO  # type: ignore

from . import config
from .species import INDEX as SPECIES_INDEX, SpeciesLabel

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ClassificationHypothesis:
    label: SpeciesLabel
    score: float


@dataclass(frozen=True)
class ClassificationResult:
    hypotheses: Sequence[ClassificationHypothesis]

    @property
    def primary(self) -> ClassificationHypothesis:
        return self.hypotheses[0]


@dataclass(frozen=True)
class DetectionResult:
    bbox: tuple[int, int, int, int]
    detection_confidence: float
    classification: ClassificationResult
    frame_timestamp: float

    @property
    def primary_label(self) -> ClassificationHypothesis:
        return self.classification.primary


class DetectionEngine:
    """Encapsulates the detector-classifier stack and preprocessing helpers."""

    def __init__(self) -> None:
        logger.info("Inicializando DetectionEngine...")
        self._device, self._predict_device_label, self._map_location = self._select_device()
        logger.info(f"Dispositivo seleccionado: {self._device} (predicción: {self._predict_device_label}, map_location: {self._map_location})")
        
        config.MODEL_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._detector = self._load_detector()
        logger.info("Detector YOLOv12 cargado correctamente")
        
        logger.info(f"Cargando clasificador SpeciesNet desde {config.CLASSIFIER_PATH}...")
        self._classifier = torch.load(config.CLASSIFIER_PATH, map_location=self._map_location, weights_only=False)
        try:
            self._classifier = self._classifier.to(self._device)
            logger.info(f"Clasificador migrado a {self._device}")
        except Exception as e:
            # Some DirectML ops may not support to(); fall back to map location tensor device.
            logger.warning(f"No se pudo migrar clasificador a {self._device}: {e}")
        self._classifier.eval()
        self._classifier_lock = threading.Lock()
        self._softmax = torch.nn.Softmax(dim=1)
        logger.info("DetectionEngine inicializado correctamente")

    def _select_device(self) -> tuple[torch.device | Any, str | None, Union[str, torch.device]]:
        if torch.cuda.is_available():
            device = torch.device("cuda")
            return device, "cuda", device
        if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
            device = torch.device("mps")
            return device, "mps", device
        try:  # pragma: no cover - optional dependency
            import torch_directml  # type: ignore

            dml_device = torch_directml.device()
            # torch.load does not accept DirectML devices; load on CPU first.
            return dml_device, None, "cpu"
        except Exception:
            pass
        device = torch.device("cpu")
        return device, "cpu", device

    def _ensure_detector_weights(self) -> None:
        if config.DETECTOR_PATH.exists():
            return
        import requests

        response = requests.get(config.DETECTOR_URL, stream=True, timeout=30)
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0)) or None
        downloaded = 0
        with config.DETECTOR_PATH.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                handle.write(chunk)
                downloaded += len(chunk)
        if total and downloaded < total:
            raise IOError("Incomplete download of detector weights")

    def _load_detector(self) -> YOLO:
        self._ensure_detector_weights()
        logger.info(f"Cargando modelo YOLOv12 desde {config.DETECTOR_PATH}...")
        model = YOLO(str(config.DETECTOR_PATH))
        try:
            model.to(self._device)
            logger.info(f"Modelo YOLO migrado a {self._device}")
        except AttributeError:  # pragma: no cover - guard for API variations
            logger.warning("No se pudo migrar YOLO con .to()")
        model.overrides["conf"] = config.DETECTION_CONFIDENCE_THRESHOLD
        model.overrides["verbose"] = False
        model.overrides["imgsz"] = 640  # Tamaño de imagen óptimo para YOLOv12
        logger.info(f"Modelo YOLOv12 configurado (conf={config.DETECTION_CONFIDENCE_THRESHOLD}, imgsz=640)")
        return model

    def infer(self, frame_bgr: np.ndarray, timestamp: float | None = None) -> List[DetectionResult]:
        """Run detection and classification on a single frame."""
        timestamp = timestamp or time.time()
        detections: List[DetectionResult] = []
        
        try:
            # Call predict with valid arguments only
            # Note: warmup is NOT a valid predict() argument, it's done automatically on first call
            results = self._detector.predict(
                source=frame_bgr,
                classes=sorted(config.ANIMAL_CLASS_IDS),
                verbose=False,
                stream=False,
                imgsz=640,  # Optimal size for YOLOv12
                conf=config.DETECTION_CONFIDENCE_THRESHOLD,
                iou=0.45,  # NMS IoU threshold
                max_det=10,  # Max 10 detections per image
                agnostic_nms=False,  # Class-specific NMS
                device=self._predict_device_label if self._predict_device_label else None,
            )
        except Exception as e:
            logger.error(f"Error en predicción YOLO: {e}")
            return detections
        if not results:
            logger.debug("YOLO no retornó resultados")
            return detections
        result = results[0]
        boxes = getattr(result, "boxes", None)
        if boxes is None or boxes.xyxy is None:
            logger.debug("No se encontraron boxes en el resultado")
            return detections
        
        xyxy = boxes.xyxy.detach().cpu().numpy()
        confidences = boxes.conf.detach().cpu().numpy()
        classes = boxes.cls.detach().cpu().numpy().astype(int)
        
        logger.debug(f"YOLO detectó {len(xyxy)} objetos totales")
        
        frame_height, frame_width = frame_bgr.shape[:2]
        raw_detections = 0
        
        for coords, conf, cls_id in zip(xyxy, confidences, classes):
            raw_detections += 1
            
            if config.ANIMAL_CLASS_IDS and cls_id not in config.ANIMAL_CLASS_IDS:
                logger.debug(f"Objeto {raw_detections}: clase {cls_id} no es animal, ignorado")
                continue
            if conf < config.DETECTION_CONFIDENCE_THRESHOLD:
                logger.debug(f"Objeto {raw_detections}: confianza {conf:.2f} muy baja, ignorado")
                continue
            
            x1, y1, x2, y2 = map(int, coords)
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(frame_width - 1, x2)
            y2 = min(frame_height - 1, y2)
            if x2 <= x1 or y2 <= y1:
                logger.debug(f"Objeto {raw_detections}: bbox inválido, ignorado")
                continue
            
            logger.info(f"Animal detectado! Clase COCO {cls_id}, confianza {conf:.2%}, bbox {(x1,y1,x2,y2)}")
            
            crop = frame_bgr[y1:y2, x1:x2]
            classification = self._classify(crop)
            detections.append(
                DetectionResult(
                    bbox=(x1, y1, x2, y2),
                    detection_confidence=conf,
                    classification=classification,
                    frame_timestamp=timestamp,
                )
            )
        detections.sort(key=lambda d: d.primary_label.score, reverse=True)
        return detections

    def _classify(self, crop_bgr: np.ndarray) -> ClassificationResult:
        rgb = cv2.cvtColor(crop_bgr, cv2.COLOR_BGR2RGB)
        prepared = self._prepare_tensor(rgb)
        with self._classifier_lock, torch.no_grad():
            logits = self._classifier(prepared)
            probs = self._softmax(logits)[0]
            topk = torch.topk(probs, k=config.CLASSIFICATION_TOP_K)
        hypotheses: List[ClassificationHypothesis] = []
        for score, class_index in zip(topk.values.cpu().tolist(), topk.indices.cpu().tolist()):
            label = SPECIES_INDEX.get(class_index)
            hypotheses.append(ClassificationHypothesis(label=label, score=float(score)))
        return ClassificationResult(hypotheses=hypotheses)

    def _prepare_tensor(self, image_rgb: np.ndarray) -> torch.Tensor:
        """Resize and normalise the crop for SpeciesNet input."""
        target = config.CLASSIFIER_INPUT_SIZE
        h, w = image_rgb.shape[:2]
        scale = min(target / h, target / w)
        new_h, new_w = max(1, int(h * scale)), max(1, int(w * scale))
        resized = cv2.resize(image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        canvas = np.zeros((target, target, 3), dtype=np.float32)
        top = (target - new_h) // 2
        left = (target - new_w) // 2
        canvas[top : top + new_h, left : left + new_w] = resized.astype(np.float32)
        tensor = torch.from_numpy(canvas / 255.0).unsqueeze(0)  # NHWC
        return tensor.to(self._device)


ENGINE = DetectionEngine()
