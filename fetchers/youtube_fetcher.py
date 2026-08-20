import subprocess
import json
import re
from pathlib import Path
from typing import Optional, List

def search_youtube_videos(keyword: str, max_results: int = 3, creative_commons_only: bool = False) -> List[dict]:
    """
    Busca videos cortos en YouTube (máximo 3 minutos para velocidad instantánea).
    """
    query = keyword
    if creative_commons_only:
        query = f"{keyword} creative commons"
        
    cmd = [
        "yt-dlp",
        f"ytsearch{max_results}:{query}",
        "--dump-json",
        "--default-search", "ytsearch",
        "--no-playlist",
        "--flat-playlist",
        "--match-filter", "duration <= 240 & duration >= 3",
        "--skip-download"
    ]
    
    videos = []
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if res.returncode == 0 and res.stdout:
            for line in res.stdout.strip().split("\n"):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    videos.append({
                        "source": "youtube",
                        "id": data.get("id"),
                        "title": data.get("title", ""),
                        "url": f"https://www.youtube.com/watch?v={data.get('id')}",
                        "duration": data.get("duration", 0)
                    })
                except Exception:
                    continue
    except Exception as e:
        print(f"[YouTubeFetcher] Error en busqueda: {e}")

    return videos

def download_youtube_clip(video_url: str, output_path: Path, start_sec: int = 2, duration_sec: int = 7) -> bool:
    """
    Descarga rápida de un clip en resolución 720p (se descarga en 2-3 segundos).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
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
        if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000:
            return True
        return False
    except Exception:
        return False
