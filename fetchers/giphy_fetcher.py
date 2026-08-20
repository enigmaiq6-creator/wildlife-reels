import requests
import re
from pathlib import Path
from typing import List, Optional

def search_tenor_clips(keyword: str, max_results: int = 5) -> List[dict]:
    """
    Busca micro-videos en Tenor/Google GIF API y extrae URLs de MP4 directo.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Endpoint público de búsqueda rápida de Tenor
    url = "https://tenor.googleapis.com/v2/search"
    params = {
        "q": keyword,
        "key": "LIVDSRZULELA", # Tenor standard public demo key
        "limit": max_results,
        "media_filter": "mp4,loopedmp4"
    }
    
    found = []
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            for item in data.get("results", []):
                media_formats = item.get("media_formats", {})
                mp4_data = media_formats.get("mp4") or media_formats.get("loopedmp4") or media_formats.get("tiny_mp4")
                if mp4_data and "url" in mp4_data:
                    found.append({
                        "source": "tenor",
                        "title": item.get("content_description", keyword),
                        "mp4_url": mp4_data["url"],
                        "duration": mp4_data.get("duration", 3.0)
                    })
    except Exception as e:
        print(f"[TenorFetcher] Error buscando en Tenor: {e}")

    return found

def download_tenor_video(mp4_url: str, output_path: Path) -> bool:
    """
    Descarga directamente el archivo MP4 desde Tenor.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(mp4_url, timeout=15, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            return output_path.exists() and output_path.stat().st_size > 500
        return False
    except Exception as e:
        print(f"[TenorFetcher] Error descargando MP4: {e}")
        return False
