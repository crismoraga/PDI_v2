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
from ..gamification import GAMIFICATION
from ..wikipedia_client import WikipediaEntry


@dataclass
class SpeciesDisplayContext:
    detection: Optional[DetectionResult]
    wikipedia: Optional[WikipediaEntry]
    history: Optional[SpeciesCaptureHistory]
    locked: bool = False


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

        # Enrichment data
        self._habitat = ttk.Label(self, text="", style="Panel.TLabel")
        self._habitat.grid(row=7, column=0, sticky="w", pady=(12, 0))

        self._diet = ttk.Label(self, text="", style="Panel.TLabel")
        self._diet.grid(row=8, column=0, sticky="w", pady=(4, 0))

        self._distribution = ttk.Label(self, text="", style="Panel.TLabel")
        self._distribution.grid(row=9, column=0, sticky="w", pady=(4, 0))

        self._conservation = ttk.Label(self, text="", style="Panel.TLabel")
        self._conservation.grid(row=10, column=0, sticky="w", pady=(4, 0))

        self._locked_label = ttk.Label(self, text="", style="Stats.TLabel")
        self._locked_label.grid(row=11, column=0, sticky="w", pady=(12, 0))

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
        # Show taxonomy quick facts
        tax = f"{label.order} — {label.family}" if label.order or label.family else ""
        if tax:
            self._details.configure(text=self._details.cget("text") + f" • {tax}")
        if wikipedia:
            summary_text = wikipedia.summary or "Sin información disponible."
            self._summary.configure(text=summary_text)
            if wikipedia.image_url:
                self._load_image(wikipedia.image_url)
            else:
                self._image_label.configure(image="", text="")
            self._link.configure(text="Abrir en Wikipedia", foreground=config.ACCENT_COLOR)
            self._link_url = wikipedia.page_url
            # Use structured fields from WikipediaEntry if available
            self._habitat.configure(text=(f"Hábitat: {wikipedia.habitat}" if getattr(wikipedia, "habitat", None) else ""))
            self._diet.configure(text=(f"Dieta: {wikipedia.diet}" if getattr(wikipedia, "diet", None) else ""))
            self._distribution.configure(text=(f"Distribución: {wikipedia.distribution}" if getattr(wikipedia, "distribution", None) else ""))
            self._conservation.configure(text=(f"Estado conservación: {getattr(wikipedia, 'conservation_status', '')}" if getattr(wikipedia, "conservation_status", None) else ""))
        else:
            self._summary.configure(text="Buscando información en Wikipedia…")
            self._image_label.configure(image="", text="")
            self._link.configure(text="")
            self._link_url = None
            self._habitat.configure(text="")
            self._diet.configure(text="")
            self._distribution.configure(text="")
            self._conservation.configure(text="")
        # Show lock status
        if getattr(context, "locked", False):
            self._locked_label.configure(text="🔒 Vista estática: presiona 'Capturar otro animal' para seguir")
        else:
            self._locked_label.configure(text="")
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
    """Displays a rolling list of captured species in Pokédex style."""

    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, style="Panel.TFrame", padding=16)
        self.columnconfigure(0, weight=1)
        
        # Heading with search/filter
        header_frame = ttk.Frame(self, style="Panel.TFrame")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        
        heading = ttk.Label(header_frame, text="📖 Pokédex de Animales", style="PanelHeading.TLabel")
        heading.pack(side="left")
        
        self._species_count_label = ttk.Label(
            header_frame,
            text="",
            style="StatsValue.TLabel",
            font=("Segoe UI", 10)
        )
        self._species_count_label.pack(side="right", padx=(12, 0))
        
        # Create scrollable canvas
        canvas = tk.Canvas(self, bg=config.PANEL_BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._items_frame = ttk.Frame(canvas, style="Panel.TFrame")
        
        self._items_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self._items_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.rowconfigure(1, weight=1)
        
        self._item_labels: list[ttk.Frame] = []

    def render(self, histories: Iterable[SpeciesCaptureHistory]) -> None:
        # Clear existing items
        for frame in self._item_labels:
            frame.destroy()
        self._item_labels.clear()
        
        sorted_histories = sorted(histories, key=lambda h: h.last_seen or "", reverse=True)
        
        # Update species count
        self._species_count_label.configure(text=f"Especies capturadas: {len(sorted_histories)}")
        
        # Get animal emoji mapping
        emoji_map = {
            "dog": "🐕", "cat": "🐈", "bird": "🦅", "horse": "🐴",
            "cow": "🐄", "sheep": "🐑", "elephant": "🐘", "bear": "🐻",
            "tiger": "🐯", "lion": "🦁", "zebra": "🦓", "giraffe": "🦒",
            "monkey": "🐵", "gorilla": "🦍", "rabbit": "🐰", "fox": "🦊",
            "wolf": "🐺", "deer": "🦌", "kangaroo": "🦘", "koala": "🐨",
            "panda": "🐼", "pig": "🐷", "frog": "🐸", "mouse": "🐭",
            "rat": "🐀", "hamster": "🐹", "bat": "🦇", "owl": "🦉",
            "eagle": "🦅", "duck": "🦆", "swan": "🦢", "parrot": "🦜",
            "penguin": "🐧", "chicken": "🐔", "peacock": "🦚"
        }
        
        for index, history in enumerate(sorted_histories):
            # Create card frame for each species
            card = ttk.Frame(self._items_frame, style="Panel.TFrame", relief="solid", borderwidth=1)
            card.pack(fill="x", pady=6, padx=4)
            
            # Top row: icon, name, count
            top_row = ttk.Frame(card, style="Panel.TFrame")
            top_row.pack(fill="x", padx=12, pady=8)
            
            # Find emoji for species
            species_emoji = "🔍"  # default
            common_lower = history.common_name.lower()
            for key, emoji in emoji_map.items():
                if key in common_lower:
                    species_emoji = emoji
                    break
            
            # Pokédex number
            number_label = ttk.Label(
                top_row,
                text=f"#{index+1:03d}",
                style="StatsValue.TLabel",
                font=("Segoe UI", 10, "bold"),
                foreground="#64748b"
            )
            number_label.pack(side="left", padx=(0, 8))
            
            # Icon
            icon_label = ttk.Label(
                top_row,
                text=species_emoji,
                font=("Segoe UI", 24),
                style="Panel.TFrame"
            )
            icon_label.pack(side="left", padx=(0, 12))
            
            # Name and scientific name
            name_frame = ttk.Frame(top_row, style="Panel.TFrame")
            name_frame.pack(side="left", fill="x", expand=True)
            
            name_label = ttk.Label(
                name_frame,
                text=history.common_name,
                style="Panel.TLabel",
                font=("Segoe UI", 13, "bold"),
                foreground="#1e293b"
            )
            name_label.pack(anchor="w")
            
            scientific_label = ttk.Label(
                name_frame,
                text=history.scientific_name,
                style="Panel.TLabel",
                font=("Segoe UI", 9, "italic"),
                foreground="#64748b"
            )
            scientific_label.pack(anchor="w")
            
            # Capture count badge
            count_label = ttk.Label(
                top_row,
                text=f"✕ {history.seen_count}",
                style="Achievement.TLabel",
                font=("Segoe UI", 12, "bold")
            )
            count_label.pack(side="right")
            
            # Bottom row: stats
            stats_row = ttk.Frame(card, style="Panel.TFrame")
            stats_row.pack(fill="x", padx=12, pady=(0, 8))
            
            # Last seen
            last_seen = history.last_seen or "Desconocido"
            if history.last_seen:
                try:
                    from datetime import datetime, timezone
                    last_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    delta = now - last_dt
                    
                    if delta.days > 0:
                        last_seen = f"Hace {delta.days} día{'s' if delta.days > 1 else ''}"
                    elif delta.seconds >= 3600:
                        hours = delta.seconds // 3600
                        last_seen = f"Hace {hours} hora{'s' if hours > 1 else ''}"
                    elif delta.seconds >= 60:
                        minutes = delta.seconds // 60
                        last_seen = f"Hace {minutes} min"
                    else:
                        last_seen = "Hace unos segundos"
                except Exception:
                    pass
            
            seen_label = ttk.Label(
                stats_row,
                text=f"⏰ {last_seen}",
                style="Panel.TLabel",
                font=("Segoe UI", 9),
                foreground="#475569"
            )
            seen_label.pack(side="left", padx=(0, 16))
            
            # Location
            location = history.last_location or "Ubicación desconocida"
            loc_label = ttk.Label(
                stats_row,
                text=f"📍 {location}",
                style="Location.TLabel",
                font=("Segoe UI", 9)
            )
            loc_label.pack(side="left")
            
            self._item_labels.append(card)


__all__ = [
    "SpeciesDisplayContext",
    "SpeciesInfoPanel",
    "CaptureHistoryPanel",
    "StatsPanel",
]


class StatsPanel(ttk.Frame):
    """Displays gamification stats, achievements, and top species."""
    
    def __init__(self, master: tk.Misc) -> None:
        super().__init__(master, style="Panel.TFrame", padding=16)
        self.columnconfigure(0, weight=1)
        
        # Heading
        heading = ttk.Label(self, text="📊 Avistamientos & Logros", style="PanelHeading.TLabel")
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        
        # Create scrollable frame
        canvas = tk.Canvas(self, bg=config.PANEL_BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._scrollable_frame = ttk.Frame(canvas, style="Panel.TFrame")
        
        self._scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self._scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky="nsew")
        scrollbar.grid(row=1, column=1, sticky="ns")
        
        self.rowconfigure(1, weight=1)
        
        self.update_stats()
    
    def update_stats(self) -> None:
        """Refresh statistics display."""
        # Clear existing widgets
        for widget in self._scrollable_frame.winfo_children():
            widget.destroy()
        
        # Get stats summary
        summary = GAMIFICATION.get_stats_summary()
        
        # === Overall Stats Section ===
        stats_frame = ttk.Frame(self._scrollable_frame, style="Panel.TFrame")
        stats_frame.pack(fill="x", pady=(0, 16))
        
        total_label = ttk.Label(
            stats_frame,
            text=f"🎯 Total de capturas: {summary['total_captures']}",
            style="Stats.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        total_label.pack(anchor="w", pady=2)
        
        species_label = ttk.Label(
            stats_frame,
            text=f"🦋 Especies descubiertas: {summary['unique_species']}",
            style="Stats.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        species_label.pack(anchor="w", pady=2)
        
        achievements_label = ttk.Label(
            stats_frame,
            text=f"🏆 Logros desbloqueados: {summary['achievements_unlocked']}/10",
            style="Achievement.TLabel",
            font=("Segoe UI", 12, "bold")
        )
        achievements_label.pack(anchor="w", pady=2)
        
        # === Separator ===
        ttk.Separator(self._scrollable_frame, orient="horizontal").pack(fill="x", pady=12)
        
        # === Top 5 Species Section ===
        if summary['top_species']:
            top_heading = ttk.Label(
                self._scrollable_frame,
                text="⭐ Top 5 Especies Más Vistas",
                style="PanelHeading.TLabel",
                font=("Segoe UI", 11, "bold")
            )
            top_heading.pack(anchor="w", pady=(0, 8))
            
            for i, species_stat in enumerate(summary['top_species'][:5], 1):
                species_frame = ttk.Frame(self._scrollable_frame, style="Panel.TFrame")
                species_frame.pack(fill="x", pady=4)
                
                # Rank emoji
                rank_emoji = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"{i}.")
                
                rank_label = ttk.Label(
                    species_frame,
                    text=f"{rank_emoji} {species_stat['common_name']}",
                    style="Panel.TLabel",
                    font=("Segoe UI", 11, "bold")
                )
                rank_label.pack(anchor="w")
                
                stats_text = (
                    f"   Avistamientos: {species_stat['total_sightings']} • "
                    f"Última vez: {species_stat['last_seen_relative']}"
                )
                stats_label = ttk.Label(
                    species_frame,
                    text=stats_text,
                    style="Panel.TLabel",
                    font=("Segoe UI", 9)
                )
                stats_label.pack(anchor="w")
                
                if species_stat['locations']:
                    locations_text = f"   Ubicaciones: {', '.join(species_stat['locations'][:3])}"
                    if len(species_stat['locations']) > 3:
                        locations_text += f" (+{len(species_stat['locations']) - 3} más)"
                    loc_label = ttk.Label(
                        species_frame,
                        text=locations_text,
                        style="Location.TLabel",
                        font=("Segoe UI", 9)
                    )
                    loc_label.pack(anchor="w")
        
        # === Separator ===
        ttk.Separator(self._scrollable_frame, orient="horizontal").pack(fill="x", pady=12)
        
        # === Unlocked Achievements Section ===
        unlocked = GAMIFICATION.get_unlocked_achievements()
        if unlocked:
            unlocked_heading = ttk.Label(
                self._scrollable_frame,
                text="🎖️ Logros Desbloqueados",
                style="PanelHeading.TLabel",
                font=("Segoe UI", 11, "bold")
            )
            unlocked_heading.pack(anchor="w", pady=(0, 8))
            
            for achievement in unlocked:
                ach_frame = ttk.Frame(self._scrollable_frame, style="Panel.TFrame")
                ach_frame.pack(fill="x", pady=4)
                
                ach_label = ttk.Label(
                    ach_frame,
                    text=f"{achievement.icon} {achievement.name}",
                    style="Achievement.TLabel",
                    font=("Segoe UI", 11, "bold")
                )
                ach_label.pack(anchor="w")
                
                desc_label = ttk.Label(
                    ach_frame,
                    text=f"   {achievement.description}",
                    style="Panel.TLabel",
                    font=("Segoe UI", 9)
                )
                desc_label.pack(anchor="w")
                
                date_label = ttk.Label(
                    ach_frame,
                    text=f"   Desbloqueado: {achievement.unlock_date}",
                    style="StatsValue.TLabel",
                    font=("Segoe UI", 8, "italic")
                )
                date_label.pack(anchor="w")
        
        # === Locked Achievements Section ===
        locked = GAMIFICATION.get_locked_achievements()
        if locked:
            ttk.Separator(self._scrollable_frame, orient="horizontal").pack(fill="x", pady=12)
            
            locked_heading = ttk.Label(
                self._scrollable_frame,
                text="🔒 Logros Por Desbloquear",
                style="PanelHeading.TLabel",
                font=("Segoe UI", 11, "bold")
            )
            locked_heading.pack(anchor="w", pady=(0, 8))
            
            for achievement in locked:
                ach_frame = ttk.Frame(self._scrollable_frame, style="Panel.TFrame")
                ach_frame.pack(fill="x", pady=4)
                
                ach_label = ttk.Label(
                    ach_frame,
                    text=f"{achievement.icon} {achievement.name}",
                    style="Panel.TLabel",
                    font=("Segoe UI", 11)
                )
                ach_label.pack(anchor="w")
                
                desc_label = ttk.Label(
                    ach_frame,
                    text=f"   {achievement.description}",
                    style="Panel.TLabel",
                    font=("Segoe UI", 9)
                )
                desc_label.pack(anchor="w")
                
                # Progress bar
                progress_frame = ttk.Frame(ach_frame, style="Panel.TFrame")
                progress_frame.pack(fill="x", padx=20, pady=4)
                
                progress_pct = (achievement.progress / achievement.target) * 100 if achievement.target > 0 else 0
                progress_text = f"{achievement.progress}/{achievement.target}"
                
                progress_label = ttk.Label(
                    progress_frame,
                    text=f"Progreso: {progress_text} ({progress_pct:.0f}%)",
                    style="StatsValue.TLabel",
                    font=("Segoe UI", 9)
                )
                progress_label.pack(anchor="w")
