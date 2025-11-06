"""Core package for the ZDex desktop application."""

from .config import APP_NAME  # re-export for convenience
from .app import run_app

__all__ = ["APP_NAME", "run_app"]
