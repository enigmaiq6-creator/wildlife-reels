import subprocess
from pathlib import Path
from typing import Optional

def download_facebook_video(video_url: str, output_path: Path, start_sec: int = 0, duration_sec: int = 10) -> bool:
    """
    Descarga videos o Reels directamente desde URLs de Facebook usando yt-dlp.
    Soporta:
    - https://www.facebook.com/reel/...
    - https://www.facebook.com/watch/?v=...
    - https://fb.watch/...
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--socket-timeout", "15",
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", str(output_path),
        "--force-overwrites",
        video_url
    ]
    
    if start_sec > 0 or duration_sec < 60:
        time_section = f"*{start_sec:02d}-{start_sec+duration_sec:02d}"
        cmd.extend(["--download-sections", time_section])

    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
        if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 10000:
            print(f"[FacebookFetcher] [OK] Video descargado con éxito de Facebook: {output_path.name}")
            return True
        else:
            print(f"[FacebookFetcher] [!] Error descargando video de Facebook: {res.stderr[:100]}")
            return False
    except Exception as e:
        print(f"[FacebookFetcher] [!] Excepción: {e}")
        return False
