"""Centralized metrics logging utilities for ZDex."""
from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Optional

from . import config


@dataclass
class DetectionMetricsRecord:
    event: str
    timestamp: float
    species_uuid: Optional[str]
    species_name: Optional[str]
    detection_confidence: Optional[float]
    classification_score: Optional[float]
    latency_ms: float
    bbox_area: Optional[int]
    detections_in_frame: int


@dataclass
class CaptureMetricsRecord:
    event: str
    timestamp: float
    species_uuid: str
    predicted_name: str
    ground_truth_name: str
    correct: bool
    detection_confidence: float
    classification_score: float
    latency_ms: float
    location: str
    auto_capture: bool


@dataclass
class LatencyRecord:
    event: str
    timestamp: float
    stage: str
    duration_ms: float
    metadata: dict[str, Any]


class MetricsLogger:
    """Thread-safe JSONL logger for evaluation metrics."""

    def __init__(self) -> None:
        metrics_dir = config.DATA_DIR / "metrics"
        metrics_dir.mkdir(parents=True, exist_ok=True)
        self._log_path = metrics_dir / "events.jsonl"
        self._lock = threading.Lock()

    def _append(self, payload: dict[str, Any]) -> None:
        payload.setdefault("timestamp", time.time())
        line = json.dumps(payload, ensure_ascii=False)
        with self._lock:
            with self._log_path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")

    def log_detection_event(
        self,
        *,
        species_uuid: Optional[str],
        species_name: Optional[str],
        detection_confidence: Optional[float],
        classification_score: Optional[float],
        latency_ms: float,
        bbox_area: Optional[int],
        detections_in_frame: int,
    ) -> None:
        record = DetectionMetricsRecord(
            event="detection",
            timestamp=time.time(),
            species_uuid=species_uuid,
            species_name=species_name,
            detection_confidence=detection_confidence,
            classification_score=classification_score,
            latency_ms=latency_ms,
            bbox_area=bbox_area,
            detections_in_frame=detections_in_frame,
        )
        self._append(asdict(record))

    def log_capture_event(
        self,
        *,
        species_uuid: str,
        predicted_name: str,
        ground_truth_name: str,
        correct: bool,
        detection_confidence: float,
        classification_score: float,
        latency_ms: float,
        location: str,
        auto_capture: bool,
    ) -> None:
        record = CaptureMetricsRecord(
            event="capture",
            timestamp=time.time(),
            species_uuid=species_uuid,
            predicted_name=predicted_name,
            ground_truth_name=ground_truth_name,
            correct=correct,
            detection_confidence=detection_confidence,
            classification_score=classification_score,
            latency_ms=latency_ms,
            location=location,
            auto_capture=auto_capture,
        )
        self._append(asdict(record))

    def log_latency_sample(
        self,
        *,
        stage: str,
        duration_ms: float,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        record = LatencyRecord(
            event="latency",
            timestamp=time.time(),
            stage=stage,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )
        self._append(asdict(record))


METRICS = MetricsLogger()

__all__ = ["METRICS"]
