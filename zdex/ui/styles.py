"""TTK style definitions for the ZDex UI."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .. import config


def configure_styles(root: tk.Tk) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:  # pragma: no cover - depends on OS themes
        pass

    # Accent button with gradient effect
    style.configure(
        "Accent.TButton",
        background=config.ACCENT_COLOR,
        foreground="white",
        font=("Segoe UI", 14, "bold"),
        padding=12,
        borderwidth=0,
        relief="flat"
    )
    style.map(
        "Accent.TButton",
        background=[("pressed", "#7e2257"), ("active", "#d14591"), ("disabled", "#cccccc")],
        foreground=[("disabled", "#666666")]
    )
    
    # Success button (for auto-capture)
    style.configure(
        "Success.TButton",
        background="#22c55e",
        foreground="white",
        font=("Segoe UI", 12, "bold"),
        padding=10,
        borderwidth=0,
        relief="flat"
    )
    style.map(
        "Success.TButton",
        background=[("pressed", "#16a34a"), ("active", "#4ade80")]
    )

    style.configure(
        "Primary.TFrame",
        background="white",
    )
    style.configure(
        "Panel.TFrame",
        background=config.PANEL_BACKGROUND,
    )
    style.configure(
        "Header.TFrame",
        background=config.HEADER_BACKGROUND,
    )
    style.configure(
        "Header.TLabel",
        background=config.HEADER_BACKGROUND,
        foreground="white",
        font=("Segoe UI", 20, "bold"),
    )
    style.configure(
        "PanelHeading.TLabel",
        background=config.HEADER_BACKGROUND,
        foreground="white",
        font=("Segoe UI", 16, "bold"),
        padding=8,
    )
    style.configure(
        "Panel.TLabel",
        background=config.PANEL_BACKGROUND,
        foreground="#1e293b",
        font=("Segoe UI", 11),
        wraplength=320,
        justify="left",
    )
    style.configure(
        "Stats.TLabel",
        background=config.PANEL_BACKGROUND,
        foreground="#334155",
        font=("Segoe UI", 12, "bold"),
    )
    style.configure(
        "StatsValue.TLabel",
        background=config.PANEL_BACKGROUND,
        foreground="#1f2937",
        font=("Segoe UI", 12),
    )
    # Achievement label
    style.configure(
        "Achievement.TLabel",
        background=config.PANEL_BACKGROUND,
        foreground="#059669",
        font=("Segoe UI", 11, "bold"),
    )
    # Location label
    style.configure(
        "Location.TLabel",
        background=config.PANEL_BACKGROUND,
        foreground="#0891b2",
        font=("Segoe UI", 10),
    )
    
    # Notebook (Tabs) - Pokédex style
    style.configure(
        "TNotebook",
        background=config.PANEL_BACKGROUND,
        borderwidth=0,
        tabmargins=[2, 5, 2, 0]
    )
    style.configure(
        "TNotebook.Tab",
        background="#e2e8f0",
        foreground="#334155",
        padding=[20, 10],
        font=("Segoe UI", 11, "bold"),
        borderwidth=0
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", config.HEADER_BACKGROUND), ("active", "#cbd5e1")],
        foreground=[("selected", "white"), ("active", "#1e293b")],
        expand=[("selected", [1, 1, 1, 0])]
    )


__all__ = ["configure_styles"]
