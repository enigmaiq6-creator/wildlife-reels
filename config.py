import os
from pathlib import Path

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Standard video resolutions
RESOLUTIONS = {
    "vertical": {"width": 1080, "height": 1920, "aspect": "9:16"},   # Reels / TikTok / Shorts
    "horizontal": {"width": 1920, "height": 1080, "aspect": "16:9"}  # YouTube horizontal
}

# Neural Documentary Voices in Simple, Clear English
VOICES = {
    "en_narrator_clear": "en-US-ChristopherNeural", # Clear, authoritative, easy to understand
    "en_narrator_deep": "en-US-GuyNeural",          # Deep, cinematic American narrator
    "en_narrator_uk": "en-GB-RyanNeural",           # Classic BBC Earth British documentary tone
}

DEFAULT_VOICE = "en_narrator_clear"

# Classic Documentary Subtitle Configuration
SUBTITLE_CONFIG = {
    "font_name": "Arial",
    "font_size_vertical": 46,
    "margin_v_vertical": 480,       # Clear of Reels UI, page name, and audio tag
    "primary_color": "&H00FFFFFF&", # Pure White
    "highlight_color": "&H0000D4FF&",# Amber Gold
    "outline_color": "&H00000000&", # Deep Black Outline
    "outline_size": 4.0,
    "shadow_size": 2.5,
    "fade_ms": 50,                   # Snappy fade
    "perceptual_lead_s": 0.035       # 35ms perceptual acoustic lead
}

# Video and Audio Settings
VIDEO_SETTINGS = {
    "fps": 30,
    "video_bitrate": "8500k",
    "audio_bitrate": "192k",
    "music_volume": 0.12,
    "voice_volume": 1.0,
    "target_duration_range": (50, 60)
}

# Directories
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
SFX_DIR = ASSETS_DIR / "sfx"

for d in [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, MUSIC_DIR, SFX_DIR]:
    d.mkdir(parents=True, exist_ok=True)
