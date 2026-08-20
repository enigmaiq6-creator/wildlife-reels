import os
from pathlib import Path

# Directorio raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Dimensiones estándar para videos
RESOLUTIONS = {
    "vertical": {"width": 1080, "height": 1920, "aspect": "9:16"},   # Reels / TikTok / Shorts
    "horizontal": {"width": 1920, "height": 1080, "aspect": "16:9"}  # YouTube horizontal
}

# Configuración de Voces Neuronales en Español (Estilo Documental / Vida Salvaje)
VOICES = {
    "es_narrator_deep": "es-ES-AlvaroNeural",   # Voz grave, autoritaria y cinemática (Estilo BBC Earth)
    "es_narrator_latam": "es-MX-JorgeNeural",   # Voz documental neutra y cálida (Estilo NatGeo Latinoamérica)
}

DEFAULT_VOICE = "es_narrator_deep"

# Configuración de Subtítulos Estilo Documental Clásico
SUBTITLE_CONFIG = {
    "font_name": "Arial",
    "font_size_vertical": 46,
    "margin_v_vertical": 480,       # Libre de la interfaz y nombre de página de Reels
    "primary_color": "&H00FFFFFF&", # Blanco puro
    "highlight_color": "&H0000D4FF&",# Dorado ámbar
    "outline_color": "&H00000000&", # Contorno negro profundo
    "outline_size": 4.0,
    "shadow_size": 2.5,
    "fade_ms": 50,                   # Fade ágil
    "perceptual_lead_s": 0.035       # 35ms de anticipación acústica
}

# Parámetros de Video y Renderizado
VIDEO_SETTINGS = {
    "fps": 30,
    "video_bitrate": "8500k",
    "audio_bitrate": "192k",
    "music_volume": 0.12,            # Música ambiental suave de fondo
    "voice_volume": 1.0,
    "target_duration_range": (50, 60) # Rango ideal para retención y monetización
}

# Directorios de Salida y Caché
OUTPUT_DIR = BASE_DIR / "output"
TEMP_DIR = BASE_DIR / "temp"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
SFX_DIR = ASSETS_DIR / "sfx"

for d in [OUTPUT_DIR, TEMP_DIR, ASSETS_DIR, MUSIC_DIR, SFX_DIR]:
    d.mkdir(parents=True, exist_ok=True)
