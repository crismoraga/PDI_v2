"""Camera capture utilities for streaming frames into the application."""
from __future__ import annotations

import logging
import queue
import threading
import time
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np

from . import config

logger = logging.getLogger(__name__)


@dataclass
class FramePacket:
    frame: np.ndarray
    timestamp: float


class CameraController:
    """Background thread that continuously grabs frames from OpenCV."""

    def __init__(self, device_id: int = config.CAMERA_DEVICE_ID) -> None:
        self.device_id = device_id
        self.frame_queue: "queue.Queue[FramePacket]" = queue.Queue(maxsize=config.FRAME_QUEUE_SIZE)
        self.analysis_queue: "queue.Queue[FramePacket]" = queue.Queue(maxsize=config.DETECTION_QUEUE_SIZE)
        self._capture_thread: Optional[threading.Thread] = None
        self._running = threading.Event()
        self._lock = threading.Lock()
        self._capture = None  # will hold cv2.VideoCapture

    def start(self) -> None:
        if self._running.is_set():
            logger.warning("Cámara ya está corriendo")
            return
        logger.info(f"Iniciando captura de cámara (device_id={self.device_id})...")
        self._running.set()
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
        logger.info("Thread de captura iniciado")

    def stop(self) -> None:
        self._running.clear()
        if self._capture_thread and self._capture_thread.is_alive():
            self._capture_thread.join(timeout=1.5)
        with self._lock:
            if self._capture is not None:
                self._capture.release()
                self._capture = None

    def _capture_loop(self) -> None:
        logger.info("Abriendo dispositivo de video...")
        with self._lock:
            capture = cv2.VideoCapture(self.device_id)
            capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_DISPLAY_MAX_WIDTH)
            capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_DISPLAY_MAX_HEIGHT)
            capture.set(cv2.CAP_PROP_FPS, 30)
            self._capture = capture
        if not capture.isOpened():
            logger.error(f"No se pudo abrir la cámara (device_id={self.device_id})")
            self._running.clear()
            return
        logger.info("Cámara abierta correctamente. Iniciando captura de frames...")
        frame_count = 0
        while self._running.is_set():
            ret, frame = capture.read()
            if not ret:
                logger.warning("No se pudo leer frame de la cámara")
                time.sleep(0.05)
                continue
            frame_count += 1
            if frame_count % 100 == 0:
                logger.debug(f"Frames capturados: {frame_count}")
            timestamp = time.time()
            packet = FramePacket(frame=frame, timestamp=timestamp)
            self._offer(self.frame_queue, packet)
            self._offer(self.analysis_queue, packet)
        logger.info("Cerrando cámara...")
        capture.release()
        logger.info("Cámara cerrada")

    @staticmethod
    def _offer(target_queue: "queue.Queue[FramePacket]", packet: FramePacket) -> None:
        try:
            target_queue.put_nowait(packet)
        except queue.Full:
            try:
                target_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                target_queue.put_nowait(packet)
            except queue.Full:
                pass


CONTROLLER = CameraController()
