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

    style.configure(
        "Accent.TButton",
        background=config.ACCENT_COLOR,
        foreground="white",
        font=("Segoe UI", 14, "bold"),
        padding=12,
        borderwidth=0,
    )
    style.map(
        "Accent.TButton",
        background=[("pressed", "#942a6b"), ("active", "#c54d93")],
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


__all__ = ["configure_styles"]
