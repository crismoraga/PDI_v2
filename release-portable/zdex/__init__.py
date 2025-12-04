"""Core package for the ZDex desktop application."""
# Re-exporta APP_NAME y expone run_app con import perezoso para evitar cargar UI/Torch en CLIs livianos

from __future__ import annotations

from .config import APP_NAME  # re-export for convenience


def run_app(*args, **kwargs):
	"""Lazy import to avoid loading heavy UI/torch stack for CLI tools."""
	from .app import run_app as _run_app

	return _run_app(*args, **kwargs)


__all__ = ["APP_NAME", "run_app"]
