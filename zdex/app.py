"""Tkinter application launcher for ZDex."""
from __future__ import annotations

import logging
import queue
import threading
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import tkinter as tk
from tkinter import messagebox, ttk

from . import config
from .camera import CONTROLLER as CAMERA
from .data_store import STORE
from .detector import ENGINE, DetectionResult
from .pipeline import DetectionPipeline, PIPELINE
from .ui.camera_canvas import CameraCanvas
from .ui.panels import CaptureHistoryPanel, SpeciesDisplayContext, SpeciesInfoPanel
from .ui.styles import configure_styles
from .wikipedia_client import FETCHER, WikipediaEntry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ZDexApp:
    """Main application tying together the UI and detection pipeline."""

    def __init__(self) -> None:
        logger.info("Inicializando ZDex...")
        self.root = tk.Tk()
        self.root.title(f"{config.APP_NAME} — {config.APP_TAGLINE}")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        configure_styles(self.root)
        config.DATA_DIR.mkdir(parents=True, exist_ok=True)
        config.CAPTURE_IMAGE_DIR.mkdir(parents=True, exist_ok=True)

        logger.info("Inicializando cámara y pipeline de detección...")
        self.camera = CAMERA
        self.pipeline: DetectionPipeline = PIPELINE or DetectionPipeline(self.camera, ENGINE)
        if PIPELINE is None:
            from . import pipeline as pipeline_module

            pipeline_module.PIPELINE = self.pipeline

        self.executor = ThreadPoolExecutor(max_workers=3, thread_name_prefix="zdex")
        self._latest_frame = None
        self._latest_timestamp = 0.0
        self._current_detections: list[DetectionResult] = []
        self._current_detection: Optional[DetectionResult] = None
        self._current_label_uuid: Optional[str] = None
        self._wiki_future: Optional[Future[Optional[WikipediaEntry]]] = None
        self._wiki_lock = threading.Lock()
        self._current_wikipedia: Optional[WikipediaEntry] = None
        self._polling_active = False
        self._location_var = tk.StringVar(value=config.DEFAULT_LOCATION)
        self._notes_var = tk.StringVar()

        logger.info("Construyendo interfaz gráfica...")
        self._build_layout()
        self._update_history_panel()
        logger.info("ZDex inicializado correctamente. Ventana lista.")

    def _build_layout(self) -> None:
        header = ttk.Frame(self.root, style="Header.TFrame", padding=(24, 16))
        header.pack(fill="x")
        title = ttk.Label(header, text=config.APP_NAME, style="Header.TLabel")
        title.pack(side="left")
        subtitle = ttk.Label(
            header,
            text=config.APP_TAGLINE,
            style="Header.TLabel",
            font=("Segoe UI", 12),
        )
        subtitle.pack(side="left", padx=(12, 0))

        body = ttk.Frame(self.root, style="Primary.TFrame", padding=24)
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        # Camera column
        camera_column = ttk.Frame(body, style="Primary.TFrame")
        camera_column.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        camera_column.rowconfigure(0, weight=1)

        self.camera_canvas = CameraCanvas(camera_column)
        self.camera_canvas.grid(row=0, column=0, sticky="nsew")

        controls = ttk.Frame(camera_column, style="Primary.TFrame", padding=(0, 16))
        controls.grid(row=1, column=0, sticky="ew")
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        self._start_button = ttk.Button(
            controls,
            text="Iniciar cámara",
            style="Accent.TButton",
            command=self._on_start_camera,
        )
        self._start_button.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self._capture_button = ttk.Button(
            controls,
            text="¡Capturar!",
            style="Accent.TButton",
            command=self._on_capture,
            state="disabled",
        )
        self._capture_button.grid(row=0, column=1, sticky="ew")

        meta_frame = ttk.Frame(camera_column, style="Primary.TFrame", padding=(0, 4))
        meta_frame.grid(row=2, column=0, sticky="ew")
        meta_frame.columnconfigure(1, weight=1)

        ttk.Label(meta_frame, text="Ubicación", style="Panel.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Entry(meta_frame, textvariable=self._location_var).grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(8, 0),
        )

        ttk.Label(meta_frame, text="Notas", style="Panel.TLabel").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(meta_frame, textvariable=self._notes_var).grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(8, 0),
            pady=(8, 0),
        )

        # Information column
        info_column = ttk.Frame(body, style="Panel.TFrame")
        info_column.grid(row=0, column=1, sticky="nsew")
        info_column.rowconfigure(0, weight=3)
        info_column.rowconfigure(1, weight=2)

        self.species_panel = SpeciesInfoPanel(info_column)
        self.species_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 16))

        self.history_panel = CaptureHistoryPanel(info_column)
        self.history_panel.grid(row=1, column=0, sticky="nsew")

    def _on_start_camera(self) -> None:
        logger.info("Usuario presionó 'Iniciar cámara'")
        try:
            self.camera.start()
            logger.info("Cámara iniciada correctamente")
            self.pipeline.start()
            logger.info("Pipeline de detección iniciado")
            self._start_button.configure(state="disabled")
            self._capture_button.configure(state="disabled")
            if not self._polling_active:
                self._polling_active = True
                self._poll_frames()
                self._poll_detections()
                logger.info("Polling de frames y detecciones activado")
        except Exception as e:
            logger.error(f"Error al iniciar cámara: {e}", exc_info=True)
            messagebox.showerror(config.APP_NAME, f"Error al iniciar cámara:\n{e}")

    def _poll_frames(self) -> None:
        if not self._polling_active:
            return
        try:
            while True:
                packet = self.camera.frame_queue.get_nowait()
                self._latest_frame = packet.frame
                self._latest_timestamp = packet.timestamp
        except queue.Empty:
            pass
        if self._latest_frame is not None:
            self.camera_canvas.render(self._latest_frame, self._current_detections)
        self.root.after(config.POLL_INTERVAL_MS, self._poll_frames)

    def _poll_detections(self) -> None:
        if not self._polling_active:
            return
        updated = False
        try:
            while True:
                batch = self.pipeline.results_queue.get_nowait()
                self._current_detections = batch.detections
                self._current_detection = batch.detections[0] if batch.detections else None
                updated = True
        except queue.Empty:
            pass
        if updated:
            self._handle_detection_update()
        self.root.after(config.DETECTION_INTERVAL_MS, self._poll_detections)

    def _handle_detection_update(self) -> None:
        detection = self._current_detection
        history = None
        self._capture_button.configure(state="normal" if detection else "disabled")
        if detection is not None:
            label = detection.primary_label.label
            history = STORE.get_history(label)
            if label.uuid != self._current_label_uuid:
                self._current_label_uuid = label.uuid
                self._current_wikipedia = None
                self._submit_wikipedia_fetch(label.common_name, label.scientific_name)
        context = SpeciesDisplayContext(
            detection=detection,
            wikipedia=self._current_wikipedia,
            history=history,
        )
        self.species_panel.update_context(context)

    def _submit_wikipedia_fetch(self, *terms: str) -> None:
        with self._wiki_lock:
            if self._wiki_future and not self._wiki_future.done():
                self._wiki_future.cancel()
            self._wiki_future = self.executor.submit(FETCHER.fetch_for_terms, *terms)
        self.root.after(150, self._check_wikipedia_future)

    def _check_wikipedia_future(self) -> None:
        with self._wiki_lock:
            future = self._wiki_future
        if not future:
            return
        if not future.done():
            self.root.after(200, self._check_wikipedia_future)
            return
        try:
            self._current_wikipedia = future.result()
        except Exception:
            self._current_wikipedia = None
        with self._wiki_lock:
            self._wiki_future = None
        self._handle_detection_update()

    def _on_capture(self) -> None:
        detection = self._current_detection
        if detection is None or self._latest_frame is None:
            messagebox.showinfo(config.APP_NAME, "No hay detecciones para capturar aún.")
            return
        label = detection.primary_label.label
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{label.uuid}_{timestamp}.jpg"
        path = config.CAPTURE_IMAGE_DIR / filename
        success = cv2.imwrite(str(path), self._latest_frame)
        if not success:
            messagebox.showerror(config.APP_NAME, "No se pudo guardar la captura.")
            return
        location = self._location_var.get().strip() or config.DEFAULT_LOCATION
        notes = self._notes_var.get().strip() or None
        history = STORE.record_capture(
            label=label,
            confidence=detection.primary_label.score,
            image_path=Path(path),
            location=location,
            notes=notes,
        )
        self.camera_canvas.flash_capture()
        self._update_history_panel()
        messagebox.showinfo(
            config.APP_NAME,
            f"Captura guardada: {label.display_name}\nAvistamientos totales: {history.seen_count}",
        )
        # Refresh panel with history including newest capture
        context = SpeciesDisplayContext(
            detection=detection,
            wikipedia=self._current_wikipedia,
            history=history,
        )
        self.species_panel.update_context(context)
        self._notes_var.set("")

    def _update_history_panel(self) -> None:
        histories = STORE.get_all()
        self.history_panel.render(histories)

    def _on_close(self) -> None:
        self._polling_active = False
        self.pipeline.stop()
        self.camera.stop()
        with self._wiki_lock:
            if self._wiki_future:
                self._wiki_future.cancel()
        self.executor.shutdown(wait=False, cancel_futures=True)
        self.root.destroy()

    def run(self) -> None:
        logger.info("Iniciando mainloop de Tkinter...")
        self.root.mainloop()
        logger.info("Aplicación cerrada.")


def run_app() -> None:
    logger.info("=== Iniciando ZDex ===")
    try:
        app = ZDexApp()
        app.run()
    except Exception as e:
        logger.error(f"Error fatal en la aplicación: {e}", exc_info=True)
        raise


__all__ = ["run_app", "ZDexApp"]


if __name__ == "__main__":
    run_app()
