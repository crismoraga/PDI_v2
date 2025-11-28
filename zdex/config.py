"""Global configuration for the ZDex application."""
from __future__ import annotations

from pathlib import Path

APP_NAME = "ZDex"
APP_TAGLINE = "Enciclopedia Animal en Tiempo Real"

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CAPTURE_IMAGE_DIR = DATA_DIR / "captures"
CAPTURE_STORE_PATH = DATA_DIR / "captures.json"

# Model assets distributed with the workspace
CLASSIFIER_FILENAME = "full_image_88545560_22x8_v12_epoch_00153.pt"
LABELS_FILENAME = "full_image_88545560_22x8_v12_epoch_00153.labels.txt"
MODEL_INFO_FILENAME = "info.json"

CLASSIFIER_PATH = BASE_DIR / CLASSIFIER_FILENAME
LABELS_PATH = BASE_DIR / LABELS_FILENAME
MODEL_INFO_PATH = BASE_DIR / MODEL_INFO_FILENAME

MODEL_CACHE_DIR = BASE_DIR / "models"
DETECTOR_FILENAME = "yolov12m.pt"
DETECTOR_URL = "https://github.com/sunsmarterjie/yolov12/releases/download/turbo/yolov12m.pt"
DETECTOR_PATH = MODEL_CACHE_DIR / DETECTOR_FILENAME

FRAME_QUEUE_SIZE = 2
DETECTION_QUEUE_SIZE = 2
CAMERA_DEVICE_ID = 10

DETECTION_CONFIDENCE_THRESHOLD = 0.25  # Reducido para detectar más animales
CLASSIFICATION_TOP_K = 3
CLASSIFIER_INPUT_SIZE = 320  # pixels, square resize preserving aspect ratio via padding
FRAME_DISPLAY_MAX_WIDTH = 960
FRAME_DISPLAY_MAX_HEIGHT = 720

PANEL_BACKGROUND = "#f9fbff"
HEADER_BACKGROUND = "#1f84a3"
ACCENT_COLOR = "#b03a7e"
BOX_COLOR = "#22c55e"
BOX_TEXT_BG = "#16a34a"
"""Color palette tuned to loosely match the design mockups."""

POLL_INTERVAL_MS = 33  # ~30 FPS para UI más fluida
DETECTION_INTERVAL_MS = 300  # Detección cada 300ms para balance velocidad/precisión

WIKIPEDIA_LANG_PRIORITY = ("es", "en")
WIKIPEDIA_SUMMARY_CHAR_LIMIT = 600

ANALYTICS_LOG_PATH = DATA_DIR / "events.log"
DEFAULT_LOCATION = "Ubicación desconocida"

# Gamification settings
AUTO_CAPTURE_THRESHOLD_SECONDS = 5.0  # Auto-captura después de 5 segundos
STATS_FILE_PATH = DATA_DIR / "stats.json"
ACHIEVEMENTS_FILE_PATH = DATA_DIR / "achievements.json"

# Animation settings
DETECTION_PULSE_COLOR = "#22c55e"  # Verde brillante para detección activa
DETECTION_GLOW_DURATION_MS = 800  # Duración de animación de brillo
CAPTURE_ANIMATION_DURATION_MS = 1500  # Animación de captura
FADE_IN_DURATION_MS = 300  # Fade in para paneles
ANIMAL_CLASS_IDS = {
	14,  # bird
	15,  # cat
	16,  # dog
	17,  # horse
	18,  # sheep
	19,  # cow
	20,  # elephant
	21,  # bear
	22,  # zebra
	23,  # giraffe
}
