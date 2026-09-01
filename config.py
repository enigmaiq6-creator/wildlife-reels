import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Project root directory
BASE_DIR = Path(__file__).resolve().parent

# Working directories
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
FONTS_DIR = ASSETS_DIR / "fonts"
SFX_DIR = ASSETS_DIR / "sfx"
CLIPS_DIR = ASSETS_DIR / "clips"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "output"
CREDENTIALS_DIR = BASE_DIR / "credentials"
CREDENTIALS_PATH = CREDENTIALS_DIR / "gcp_service_account.json"
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "facebookbot-502117")

for folder in [ASSETS_DIR, MUSIC_DIR, FONTS_DIR, SFX_DIR, CLIPS_DIR, TEMP_DIR, OUTPUT_DIR, CREDENTIALS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Video Resolutions
RESOLUTIONS = {
    "vertical": {"width": 1080, "height": 1920, "aspect": "9:16"},    # TikTok / Shorts / Reels
    "horizontal": {"width": 1920, "height": 1080, "aspect": "16:9"}   # Standard YouTube
}

DEFAULT_ASPECT = "vertical"
DEFAULT_FPS = 30
DEFAULT_VIDEO_BITRATE = "9500k"
DEFAULT_AUDIO_BITRATE = "192k"

# Google Cloud Text-to-Speech Ultra-Realistic Studio Documentary Voice
GOOGLE_TTS_API_KEY = os.environ.get("GOOGLE_TTS_API_KEY", "AIzaSyDpdDhoXt8GDwJ_sEj-vjtd6HqVflN_vSY")

# Neural & Studio Voices in Clear Documentary English
VOICES = {
    "google_studio_male": "en-US-Studio-Q",
    "google_studio_uk": "en-GB-Studio-B",
    "google_studio_female": "en-US-Studio-O",
    "google_neural_dramatic": "en-US-Neural2-J",
    "google_neural_uk": "en-GB-Neural2-B",
    "en_narrator_clear": "en-US-ChristopherNeural",
    "en_narrator_deep": "en-US-GuyNeural",
    "en_narrator_uk": "en-GB-RyanNeural"
}

DEFAULT_VOICE = "en-US-Studio-Q"

# SUBTÍTULOS GRANDES DE ALTO IMPACTO (Mobile-First / Reels)
SUBTITLE_CONFIG = {
    "font_name": "Arial",
    "font_size_vertical": 60,        # Aumentado a tamaño 60 para máxima legibilidad
    "font_size_hook": 66,            # Tamaño 66 para ganchos
    "font_size_impact": 76,          # Tamaño 76 para palabras de impacto (BAM!, etc.)
    "margin_v_vertical": 480,        # Libre de nombres de página y barras de Reels
    "primary_color": "&H00FFFFFF&",  # Blanco puro
    "highlight_color": "&H0000D4FF&", # Dorado ámbar brillante
    "outline_color": "&H00000000&",  # Contorno negro grueso
    "outline_size": 5.2,             # Borde reforzado para contraste perfecto
    "shadow_size": 3.0,
    "fade_ms": 40,
    "perceptual_lead_s": 0.035
}

# RITMO DINÁMICO MULTI-CLIP (Cambio de tomas cada 2.5 - 3.5 segundos)
PACING_SETTINGS = {
    "max_shot_duration": 3.5,        # Ninguna toma dura más de 3.5 segundos (cero monotonía)
    "min_shot_duration": 2.0
}

VIDEO_SETTINGS = {
    "fps": 30,
    "video_bitrate": "9500k",
    "audio_bitrate": "192k",
    "music_volume": 0.12,
    "voice_volume": 1.0,
    "target_duration_range": (50, 55)
}

# API Keys
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "qbp4umsXdbrpdEUx2NgVdlCudGEhtJ7rXgZZ5Uql2Euo0S1y5LxpQ4zm")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "57182356-903be23968c4863c98e1f2f78")
