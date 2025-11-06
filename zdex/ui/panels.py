"""UI panels for the ZDex interface."""
from __future__ import annotations

import io
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk
from typing import Iterable, Optional, Sequence

import requests
from PIL import Image, ImageTk

from .. import config
from ..data_store import CaptureStore, SpeciesCaptureHistory
from ..detector import DetectionResult
from ..wikipedia_client import WikipediaEntry


@dataclass
class SpeciesDisplayContext:
    detection: Optional[DetectionResult]
    wikipedia: Optional[WikipediaEntry]
    history: Optional[SpeciesCaptureHistory]


class SpeciesInfoPanel(ttk.Frame):
    """Shows details for the selected detection along with Wikipedia info."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, style="Panel.TFrame", padding=16)
        self.columnconfigure(0, weight=1)
        self._image_ref: Optional[ImageTk.PhotoImage] = None

        heading = ttk.Label(self, text="Ficha de especie", style="PanelHeading.TLabel")
        heading.grid(row=0, column=0, sticky="ew")

        self._title = ttk.Label(self, text="Esperando detección…", style="Panel.TLabel")
        self._title.grid(row=1, column=0, sticky="w", pady=(12, 2))

        self._details = ttk.Label(self, text="", style="Panel.TLabel")
        self._details.grid(row=2, column=0, sticky="w")

        self._summary = ttk.Label(self, text="", style="Panel.TLabel")
        self._summary.grid(row=3, column=0, sticky="w", pady=(12, 0))

        self._image_label = ttk.Label(self, style="Panel.TLabel")
        self._image_label.grid(row=4, column=0, sticky="ew", pady=(12, 0))

        self._link = ttk.Label(self, text="", style="StatsValue.TLabel", cursor="hand2")
        self._link.grid(row=5, column=0, sticky="w", pady=(12, 0))
        self._link.bind("<Button-1>", self._open_link)
        self._link_url: Optional[str] = None

        self._history_stats = ttk.Label(self, text="", style="Panel.TLabel")
        self._history_stats.grid(row=6, column=0, sticky="w", pady=(12, 0))

    def clear(self) -> None:
        self._title.configure(text="Esperando detección…")
        self._details.configure(text="")
        self._summary.configure(text="")
        self._image_label.configure(image="", text="")
        self._image_ref = None
        self._link.configure(text="")
        self._link_url = None
        self._history_stats.configure(text="")

    def update_context(self, context: SpeciesDisplayContext) -> None:
        detection = context.detection
        wikipedia = context.wikipedia
        history = context.history
        if detection is None:
            self.clear()
            return
        label = detection.primary_label.label
        confidence = detection.primary_label.score
        self._title.configure(text=f"{label.display_name}")
        self._details.configure(
            text=f"Confianza {confidence:.0%} • {label.scientific_name}"
        )
        if wikipedia:
            summary_text = wikipedia.summary or "Sin información disponible."
            self._summary.configure(text=summary_text)
            if wikipedia.image_url:
                self._load_image(wikipedia.image_url)
            else:
                self._image_label.configure(image="", text="")
            self._link.configure(text="Abrir en Wikipedia", foreground=config.ACCENT_COLOR)
            self._link_url = wikipedia.page_url
        else:
            self._summary.configure(text="Buscando información en Wikipedia…")
            self._image_label.configure(image="", text="")
            self._link.configure(text="")
            self._link_url = None
        if history:
            last_notes = history.last_notes or "Sin notas"
            stats = (
                f"Avistamientos: {history.seen_count}\n"
                f"Última ubicación: {history.last_location or '—'}\n"
                f"Última nota: {last_notes}"
            )
            self._history_stats.configure(text=stats)
        else:
            self._history_stats.configure(text="Sin capturas previas.")

    def _load_image(self, url: str) -> None:
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            raw = io.BytesIO(response.content)
            image = Image.open(raw)
            max_width = 320
            max_height = 200
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self._image_label.configure(image=photo)
            self._image_ref = photo
        except Exception:
            self._image_label.configure(image="", text="")
            self._image_ref = None

    def _open_link(self, event: tk.Event[tk.Misc]) -> None:  # pragma: no cover - UI only
        if not self._link_url:
            return
        import webbrowser

        webbrowser.open_new(self._link_url)


class CaptureHistoryPanel(ttk.Frame):
    """Displays a rolling list of captured events."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, style="Panel.TFrame", padding=16)
        self.columnconfigure(0, weight=1)
        heading = ttk.Label(self, text="Historial", style="PanelHeading.TLabel")
        heading.grid(row=0, column=0, sticky="ew")
        self._items_frame = ttk.Frame(self, style="Panel.TFrame")
        self._items_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self._item_labels: list[ttk.Label] = []

    def render(self, histories: Iterable[SpeciesCaptureHistory]) -> None:
        for label in self._item_labels:
            label.destroy()
        self._item_labels.clear()
        for index, history in enumerate(sorted(histories, key=lambda h: h.last_seen or "", reverse=True)):
            text = self._format_history(history)
            entry = ttk.Label(self._items_frame, text=text, style="Panel.TLabel")
            entry.grid(row=index, column=0, sticky="w", pady=6)
            self._item_labels.append(entry)

    def _format_history(self, history: SpeciesCaptureHistory) -> str:
        last_seen = history.last_seen or "Sin registros"
        location = history.last_location or "Ubicación desconocida"
        notes = history.last_notes or "Sin notas"
        return (
            f"{history.common_name} • {history.seen_count} capturas\n"
            f"Última: {last_seen}\n"
            f"{location}\n"
            f"Nota: {notes}"
        )


__all__ = [
    "SpeciesDisplayContext",
    "SpeciesInfoPanel",
    "CaptureHistoryPanel",
]
