import subprocess
import json
import re
from pathlib import Path
from typing import Optional, List

def search_tiktok_clips(keyword: str, max_results: int = 3) -> List[dict]:
    """
    Busca clips verticales estilo TikTok / Shorts sobre la palabra clave.
    """
    query = f"{keyword} tiktok"
    cmd = [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--dump-json",
        "--default-search", "ytsearch",
        "--no-playlist",
        "--flat-playlist",
        "--match-filter", "duration <= 60 & duration >= 3",
        "--skip-download"
    ]
    
    found = []
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if res.returncode == 0 and res.stdout:
            for line in res.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    found.append({
                        "source": "tiktok_shorts",
                        "id": data.get("id"),
                        "title": data.get("title", ""),
                        "url": f"https://www.youtube.com/watch?v={data.get('id')}",
                        "duration": data.get("duration", 0)
                    })
                except Exception:
                    continue
    except Exception as e:
        print(f"[TikTokFetcher] Error en busqueda: {e}")

    return found

def download_tiktok_video(video_url: str, output_path: Path, start_sec: int = 2, duration_sec: int = 7) -> bool:
    """
    Descarga un video de TikTok o clip vertical directo en formato MP4.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Si es un enlace de TikTok directo
    if "tiktok.com" in video_url:
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--socket-timeout", "4",
            "-f", "best[height<=720]/best",
            "--merge-output-format", "mp4",
            "-o", str(output_path),
            "--force-overwrites",
            video_url
        ]
    else:
        end_sec = start_sec + duration_sec
        time_section = f"*{start_sec:02d}-{end_sec:02d}"
        cmd = [
            "yt-dlp",
            "--no-playlist",
            "--socket-timeout", "4",
            "-f", "best[height<=720]/best",
            "--download-sections", time_section,
            "--merge-output-format", "mp4",
            "-o", str(output_path),
            "--force-overwrites",
            video_url
        ]
    
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
        return res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000
    except Exception:
        return False
