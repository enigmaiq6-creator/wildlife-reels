import requests
from pathlib import Path
from typing import List
from config import PIXABAY_API_KEY

def search_pixabay_videos(keyword: str, max_results: int = 3) -> List[dict]:
    """
    Busca videos de alta calidad en Pixabay con la clave oficial de API y obtiene enlaces directos MP4 en <300ms.
    """
    if not PIXABAY_API_KEY:
        return []

    url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": keyword,
        "per_page": max_results
    }
    
    found = []
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            for hit in data.get("hits", []):
                videos = hit.get("videos", {})
                v_data = videos.get("medium") or videos.get("large") or videos.get("small") or videos.get("tiny")
                if v_data and "url" in v_data and v_data["url"]:
                    found.append({
                        "source": "pixabay",
                        "title": hit.get("tags", keyword),
                        "video_url": v_data["url"],
                        "duration": hit.get("duration", 5)
                    })
    except Exception as e:
        print(f"[PixabayFetcher] Error: {e}")
        
    return found

def download_pixabay_video(video_url: str, output_path: Path) -> bool:
    """Descarga instantánea directa de CDN de Pixabay."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        headers = {"User-Agent": "CuriosityApp/1.0 (educational)"}
        resp = requests.get(video_url, headers=headers, timeout=10, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=32768):
                    f.write(chunk)
            return output_path.exists() and output_path.stat().st_size > 1000
        return False
    except Exception as e:
        print(f"[PixabayFetcher] Error descargando: {e}")
        return False
