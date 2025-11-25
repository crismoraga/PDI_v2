"""Core package for the ZDex desktop application."""

from __future__ import annotations

from .config import APP_NAME  # re-export for convenience


def run_app(*args, **kwargs):
	"""Lazy import to avoid loading heavy UI/torch stack for CLI tools."""
	from .app import run_app as _run_app

	return _run_app(*args, **kwargs)


__all__ = ["APP_NAME", "run_app"]
