"""Tkinter application launcher for ZDex."""
from __future__ import annotations

import logging
import queue
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from . import config
from .camera import CONTROLLER as CAMERA
from .data_store import STORE
from .detector import ENGINE, DetectionResult
from .gamification import GAMIFICATION, Achievement
from .geolocation import GEOLOCATOR, Location
from .metrics import METRICS
from .pipeline import DetectionPipeline, PIPELINE
from .ui.camera_canvas import CameraCanvas
from .ui.panels import CaptureHistoryPanel, SpeciesDisplayContext, SpeciesInfoPanel, StatsPanel
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

        # Get current location automatically
        logger.info("Obteniendo ubicación automática...")
        self._current_location = GEOLOCATOR.get_current_location()
        if self._current_location:
            logger.info(f"Ubicación detectada: {self._current_location.display_name}")
        else:
            logger.warning("No se pudo obtener ubicación automática")
            self._current_location = Location("", "", config.DEFAULT_LOCATION, 0.0, 0.0)

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
        self._location_var = tk.StringVar(value=self._current_location.display_name)
        self._notes_var = tk.StringVar()
        
        # Auto-capture tracking
        self._detection_start_time: Optional[float] = None
        self._last_detected_species: Optional[str] = None
        self._auto_capture_triggered = False

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

        # Information column - Create Notebook for tab navigation
        info_column = ttk.Frame(body, style="Panel.TFrame")
        info_column.grid(row=0, column=1, sticky="nsew")
        
        # Create notebook (tabs) for Pokédex-style navigation
        self.info_notebook = ttk.Notebook(info_column)
        self.info_notebook.pack(fill="both", expand=True)
        
        # Tab 1: Species Info (current detection)
        species_tab = ttk.Frame(self.info_notebook, style="Panel.TFrame")
        self.info_notebook.add(species_tab, text="📷 Detección Actual")
        
        self.species_panel = SpeciesInfoPanel(species_tab)
        self.species_panel.pack(fill="both", expand=True)
        
        # Tab 2: Pokédex (History)
        history_tab = ttk.Frame(self.info_notebook, style="Panel.TFrame")
        self.info_notebook.add(history_tab, text="📖 Pokédex")
        
        self.history_panel = CaptureHistoryPanel(history_tab)
        self.history_panel.pack(fill="both", expand=True)
        
        # Tab 3: Achievements & Stats
        stats_tab = ttk.Frame(self.info_notebook, style="Panel.TFrame")
        self.info_notebook.add(stats_tab, text="🏆 Logros")
        
        self.stats_panel = StatsPanel(stats_tab)
        self.stats_panel.pack(fill="both", expand=True)

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
        
        # Auto-capture logic
        if self._current_detection:
            species_name = self._current_detection.primary_label.label.species
            current_time = time.time()
            
            # Same species detected continuously
            if self._last_detected_species == species_name:
                if self._detection_start_time is None:
                    self._detection_start_time = current_time
                else:
                    elapsed = current_time - self._detection_start_time
                    # Update countdown on canvas
                    remaining = max(0, config.AUTO_CAPTURE_THRESHOLD_SECONDS - elapsed)
                    self.camera_canvas.set_auto_capture_countdown(remaining)
                    
                    # Trigger auto-capture after threshold
                    if elapsed >= config.AUTO_CAPTURE_THRESHOLD_SECONDS and not self._auto_capture_triggered:
                        logger.info(f"Auto-captura activada después de {elapsed:.1f}s")
                        self._auto_capture_triggered = True
                        self.root.after(100, self._on_capture)
            else:
                # New species detected, reset timer
                self._last_detected_species = species_name
                self._detection_start_time = current_time
                self._auto_capture_triggered = False
                self.camera_canvas.set_auto_capture_countdown(None)
        else:
            # No detection, reset everything
            if self._last_detected_species is not None:
                self._last_detected_species = None
                self._detection_start_time = None
                self._auto_capture_triggered = False
                self.camera_canvas.set_auto_capture_countdown(None)
        
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
            # Only fetch Wikipedia if species changed (persistence)
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
        auto_capture = self._auto_capture_triggered
        label = detection.primary_label.label
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{label.uuid}_{timestamp}.jpg"
        path = config.CAPTURE_IMAGE_DIR / filename
        success = cv2.imwrite(str(path), self._latest_frame)
        if not success:
            messagebox.showerror(config.APP_NAME, "No se pudo guardar la captura.")
            return
        frame_ts = getattr(detection, "frame_timestamp", None)
        capture_latency_ms = 0.0
        if frame_ts is not None:
            capture_latency_ms = max(0.0, (time.time() - frame_ts) * 1000.0)
        location = self._location_var.get().strip() or self._current_location.display_name
        notes = self._notes_var.get().strip() or None
        history = STORE.record_capture(
            label=label,
            confidence=detection.primary_label.score,
            image_path=Path(path),
            location=location,
            notes=notes,
        )
        predicted_name = label.display_name
        prompt = (
            f"¿La especie detectada coincide con {predicted_name}?\n"
            "Selecciona 'Sí' si el modelo acertó o 'No' para corregir."
        )
        prediction_correct = messagebox.askyesno(config.APP_NAME, prompt)
        ground_truth_name = predicted_name
        if not prediction_correct:
            correction = simpledialog.askstring(
                config.APP_NAME,
                "Ingresa el nombre correcto para registrar la precisión:",
                initialvalue=predicted_name,
            )
            if correction:
                ground_truth_name = correction.strip()
            else:
                ground_truth_name = "Desconocido"
        METRICS.log_capture_event(
            species_uuid=label.uuid,
            predicted_name=predicted_name,
            ground_truth_name=ground_truth_name,
            correct=prediction_correct,
            detection_confidence=detection.detection_confidence,
            classification_score=detection.primary_label.score,
            latency_ms=capture_latency_ms,
            location=location,
            auto_capture=auto_capture,
        )
        
        # Record sighting in gamification system
        newly_unlocked = GAMIFICATION.record_sighting(
            species_name=label.species,
            common_name=label.common_name,
            location=location,
            confidence=detection.primary_label.score
        )
        
        # Flash effect
        self.camera_canvas.flash_capture()
        self._update_history_panel()
        
        # Show achievement notifications
        if newly_unlocked:
            self._show_achievement_notifications(newly_unlocked)
        
        # Regular capture notification
        messagebox.showinfo(
            config.APP_NAME,
            f"✅ Captura guardada: {label.display_name}\nAvistamientos totales: {history.seen_count}",
        )
        
        # Refresh panel with history including newest capture
        context = SpeciesDisplayContext(
            detection=detection,
            wikipedia=self._current_wikipedia,
            history=history,
        )
        self.species_panel.update_context(context)
        self._notes_var.set("")
        
        # Reset auto-capture state
        self._auto_capture_triggered = False
        self._detection_start_time = None

    def _show_achievement_notifications(self, achievements: list[Achievement]) -> None:
        """Display achievement unlock notifications in a custom styled window."""
        for achievement in achievements:
            # Create custom notification window
            notif = tk.Toplevel(self.root)
            notif.title("¡Logro Desbloqueado!")
            notif.geometry("400x200")
            notif.resizable(False, False)
            
            # Configure window style
            notif.configure(bg="#f9fbff")
            
            # Center on screen
            notif.update_idletasks()
            x = (notif.winfo_screenwidth() // 2) - (400 // 2)
            y = (notif.winfo_screenheight() // 2) - (200 // 2)
            notif.geometry(f"+{x}+{y}")
            
            # Content frame
            frame = ttk.Frame(notif, style="Primary.TFrame", padding=24)
            frame.pack(fill="both", expand=True)
            
            # Icon and title
            header = ttk.Frame(frame, style="Primary.TFrame")
            header.pack(fill="x", pady=(0, 16))
            
            icon_label = ttk.Label(
                header,
                text=achievement.icon,
                font=("Segoe UI", 48),
                style="Primary.TFrame"
            )
            icon_label.pack(side="left", padx=(0, 16))
            
            title_label = ttk.Label(
                header,
                text=achievement.name,
                style="Achievement.TLabel",
                font=("Segoe UI", 18, "bold")
            )
            title_label.pack(side="left", fill="x", expand=True)
            
            # Description
            desc_label = ttk.Label(
                frame,
                text=achievement.description,
                style="Panel.TLabel",
                font=("Segoe UI", 12),
                wraplength=350
            )
            desc_label.pack(fill="x", pady=(0, 16))
            
            # Close button
            close_btn = ttk.Button(
                frame,
                text="¡Genial!",
                style="Accent.TButton",
                command=notif.destroy
            )
            close_btn.pack()
            
            # Auto-close after 5 seconds
            notif.after(5000, notif.destroy)
            
            # Play focus animation
            notif.focus_force()
            logger.info(f"🏆 Logro desbloqueado: {achievement.name}")

    def _update_history_panel(self) -> None:
        """Update both history and stats panels."""
        histories = STORE.get_all()
        self.history_panel.render(histories)
        self.stats_panel.update_stats()

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
