import requests
from pathlib import Path
from typing import List, Optional
from config import PEXELS_API_KEY

def search_pexels_videos(keyword: str, orientation: str = "portrait", max_results: int = 3) -> List[dict]:
    """
    Busca videos HD y 4K en Pexels API oficial y extrae URLs directas MP4 en <300ms.
    """
    if not PEXELS_API_KEY:
        return []
        
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    url = f"https://api.pexels.com/videos/search?query={keyword}&orientation={orientation}&per_page={max_results}"
    
    found = []
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            for v in data.get("videos", []):
                files = v.get("video_files", [])
                # Pexels almacena tags en v.get('url') o v.get('tags')
                video_url_slug = v.get("url", "").lower()
                
                hd_file = None
                for f in files:
                    if f.get("quality") == "hd" and f.get("file_type") == "video/mp4":
                        hd_file = f.get("link")
                        break
                if not hd_file and files:
                    hd_file = files[0].get("link")
                    
                if hd_file:
                    found.append({
                        "source": "pexels",
                        "title": video_url_slug,
                        "tags": video_url_slug,
                        "video_url": hd_file,
                        "duration": v.get("duration", 5)
                    })
    except Exception as e:
        print(f"[PexelsFetcher] Error: {e}")
        
    return found

def download_pexels_video(video_url: str, output_path: Path) -> bool:
    """Descarga directa de CDN de alta velocidad de Pexels."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(video_url, timeout=12, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=32768):
                    f.write(chunk)
            return output_path.exists() and output_path.stat().st_size > 1000
        return False
    except Exception as e:
        print(f"[PexelsFetcher] Error descargando: {e}")
        return False
