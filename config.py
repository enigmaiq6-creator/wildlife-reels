import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Working directories
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"
SFX_DIR = ASSETS_DIR / "sfx"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"

for folder in [ASSETS_DIR, MUSIC_DIR, FONTS_DIR, SFX_DIR, TEMP_DIR, OUTPUT_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Video Resolutions
RESOLUTIONS = {
    "vertical": {"width": 1080, "height": 1920, "aspect": "9:16"},    # TikTok / Shorts / Reels
    "horizontal": {"width": 1920, "height": 1080, "aspect": "16:9"}   # Standard YouTube
}

DEFAULT_ASPECT = "vertical"
DEFAULT_FPS = 30
DEFAULT_VIDEO_BITRATE = "8500k"
DEFAULT_AUDIO_BITRATE = "192k"

# Neural Voices in Clear English
VOICES = {
    "en_narrator_clear": "en-US-ChristopherNeural",
    "en_narrator_deep": "en-US-GuyNeural",
    "en_narrator_uk": "en-GB-RyanNeural"
}

DEFAULT_VOICE = "en-US-ChristopherNeural"

# Classic Documentary Subtitle Settings
SUBTITLE_CONFIG = {
    "font_name": "Arial",
    "font_size_vertical": 46,
    "margin_v_vertical": 480,       # Clears Reels page name and audio UI
    "primary_color": "&H00FFFFFF&", # Pure White
    "highlight_color": "&H0000D4FF&",# Amber Gold
    "outline_color": "&H00000000&", # Deep Black Outline
    "outline_size": 4.0,
    "shadow_size": 2.5,
    "fade_ms": 50,                   # Snappy fade
    "perceptual_lead_s": 0.035       # 35ms perceptual lead
}

VIDEO_SETTINGS = {
    "fps": 30,
    "video_bitrate": "8500k",
    "audio_bitrate": "192k",
    "music_volume": 0.12,
    "voice_volume": 1.0,
    "target_duration_range": (50, 60)
}

# API Keys
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "qbp4umsXdbrpdEUx2NgVdlCudGEhtJ7rXgZZ5Uql2Euo0S1y5LxpQ4zm")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "57182356-903be23968c4863c98e1f2f78")
