import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# LLM Settings
LLM_BASE_URL = "http://169.254.123.39:1234/v1"
LLM_API_KEY = "lm-studio" # Usually ignored by LM Studio
LLM_MODEL = "qwen/qwen3-vl-30b" # Adjust as needed based on what's loaded

# Marker Settings
MARKER_LANGS = ["tr"] # Turkish
