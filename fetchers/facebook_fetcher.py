import sys
import argparse
import subprocess
from pathlib import Path

# Asegurar codificación UTF-8 en Windows
try:
    if sys.platform.startswith("win"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

# Directorio de clips locales del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
CLIPS_DIR = BASE_DIR / "assets" / "clips"
CLIPS_DIR.mkdir(parents=True, exist_ok=True)

def download_facebook_clip(video_url: str, animal_name: str, clip_index: int = 1) -> bool:
    """
    Descarga un video o Reel de Facebook en máxima resolución y lo guarda
    directamente en assets/clips/ para ser usado automáticamente por el motor de video.
    """
    clean_name = animal_name.lower().strip().replace(" ", "_")
    output_filename = f"{clean_name}_{clip_index:02d}.mp4"
    output_path = CLIPS_DIR / output_filename
    
    print(f"\n[FacebookDownloader] Descargando video de Facebook: {video_url}...")
    print(f"[FacebookDownloader] Destino: {output_path}...")

    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--socket-timeout", "20",
        "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
        "--merge-output-format", "mp4",
        "-o", str(output_path),
        "--force-overwrites",
        video_url
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 10000:
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"[FacebookDownloader] [¡ÉXITO TOTAL! 🚀] Video guardado ({size_mb:.2f} MB): {output_filename}")
            return True
        else:
            print(f"[FacebookDownloader] [!] Error descargando video de Facebook:\n{res.stderr[:200]}")
            return False
    except Exception as e:
        print(f"[FacebookDownloader] [!] Excepción: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descargador de Videos de Facebook para Wildlife Engine")
    parser.add_argument("--url", type=str, required=True, help="URL del video o Reel de Facebook")
    parser.add_argument("--name", type=str, required=True, help="Nombre del animal (ej: shoebill, jaguar, eagle)")
    parser.add_argument("--idx", type=int, default=1, help="Número de clip (1, 2, 3...)")
    args = parser.parse_args()

    download_facebook_clip(args.url, args.name, args.idx)
