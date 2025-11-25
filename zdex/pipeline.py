"""High-level orchestration of the camera stream and detection engine."""
from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass
from typing import List, Optional

from . import config
from .camera import CameraController, FramePacket
from .detector import DetectionEngine, DetectionResult
from .metrics import METRICS

logger = logging.getLogger(__name__)


@dataclass
class DetectionBatch:
    timestamp: float
    frame_shape: tuple[int, int, int]
    detections: List[DetectionResult]


class DetectionPipeline:
    """Consumes camera frames and emits detection batches asynchronously."""

    def __init__(
        self,
        camera: CameraController,
        engine: DetectionEngine,
    ) -> None:
        self._camera = camera
        self._engine = engine
        self.results_queue: "queue.Queue[DetectionBatch]" = queue.Queue(maxsize=config.DETECTION_QUEUE_SIZE)
        self._worker: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._last_inference_ts = 0.0

    def start(self) -> None:
        if self._running.is_set():
            logger.warning("Pipeline ya está corriendo")
            return
        logger.info("Iniciando pipeline de detección...")
        self._running.set()
        self._worker = threading.Thread(target=self._loop, daemon=True)
        self._worker.start()
        logger.info("Pipeline iniciado correctamente")

    def stop(self) -> None:
        logger.info("Deteniendo pipeline...")
        self._running.clear()
        if self._worker and self._worker.is_alive():
            self._worker.join(timeout=1.5)
        logger.info("Pipeline detenido")

    def _loop(self) -> None:
        logger.info("Loop de detección iniciado")
        warmup_done = False
        inference_count = 0
        
        while self._running.is_set():
            try:
                packet: FramePacket = self._camera.analysis_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            
            now = time.time()
            if now - self._last_inference_ts < config.DETECTION_INTERVAL_MS / 1000.0:
                continue
            
            self._last_inference_ts = now
            
            try:
                # Ejecutar detección
                detections = self._engine.infer(packet.frame, packet.timestamp)
                inference_count += 1
                latency_ms = (time.time() - packet.timestamp) * 1000.0
                METRICS.log_latency_sample(
                    stage="inference",
                    duration_ms=latency_ms,
                    metadata={
                        "detections": len(detections),
                        "frame_shape": packet.frame.shape if packet.frame is not None else None,
                    },
                )
                
                if not warmup_done:
                    logger.info(f"Primera inferencia exitosa! Detectados {len(detections)} objetos")
                    warmup_done = True
                
                if inference_count % 20 == 0:
                    logger.debug(f"Inferencias ejecutadas: {inference_count}, última detección: {len(detections)} objetos")
                
                if detections:
                    logger.info(
                        f"¡Animal detectado! {len(detections)} detección(es): "
                        f"{[d.primary_label.label.common_name for d in detections]}"
                    )
                    top = detections[0]
                    bbox = top.bbox
                    area = max(0, (bbox[2] - bbox[0])) * max(0, (bbox[3] - bbox[1]))
                    METRICS.log_detection_event(
                        species_uuid=top.primary_label.label.uuid,
                        species_name=top.primary_label.label.display_name,
                        detection_confidence=top.detection_confidence,
                        classification_score=top.primary_label.score,
                        latency_ms=latency_ms,
                        bbox_area=area,
                        detections_in_frame=len(detections),
                    )
                
                batch = DetectionBatch(
                    timestamp=packet.timestamp,
                    frame_shape=packet.frame.shape,
                    detections=detections,
                )
                self._offer(batch)
                
            except Exception as e:
                logger.error(f"Error en inferencia (continúa ejecutando): {e}", exc_info=True)
                # Publicar batch vacío para mantener UI responsiva
                batch = DetectionBatch(
                    timestamp=packet.timestamp,
                    frame_shape=packet.frame.shape,
                    detections=[],
                )
                self._offer(batch)
        
        logger.info("Loop de detección finalizado")

    def _offer(self, batch: DetectionBatch) -> None:
        try:
            self.results_queue.put_nowait(batch)
        except queue.Full:
            try:
                self.results_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.results_queue.put_nowait(batch)
            except queue.Full:
                pass


PIPELINE: Optional[DetectionPipeline] = None
