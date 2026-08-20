import requests
from pathlib import Path
from typing import List, Optional
from config import PEXELS_API_KEY

HEADERS = {
    "Authorization": PEXELS_API_KEY,
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def search_pexels_videos(keyword: str, orientation: str = "portrait", max_results: int = 8) -> List[dict]:
    """
    Busca videos HD y 4K en Pexels API oficial con User-Agent verificado.
    """
    if not PEXELS_API_KEY:
        return []
        
    url = f"https://api.pexels.com/videos/search?query={keyword}&orientation={orientation}&per_page={max_results}"
    
    found = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            videos = data.get("videos", [])
            
            # Si no encontró en portrait, buscar en todas las orientaciones
            if not videos and orientation == "portrait":
                url_all = f"https://api.pexels.com/videos/search?query={keyword}&per_page={max_results}"
                resp_all = requests.get(url_all, headers=HEADERS, timeout=8)
                if resp_all.status_code == 200:
                    videos = resp_all.json().get("videos", [])

            for v in videos:
                files = v.get("video_files", [])
                video_url_slug = v.get("url", "").lower()
                
                # Priorizar video HD/4K
                hd_file = None
                for f in sorted(files, key=lambda x: (x.get("width", 0) * x.get("height", 0)), reverse=True):
                    if f.get("file_type") == "video/mp4" and f.get("link"):
                        hd_file = f.get("link")
                        break
                        
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
        resp = requests.get(video_url, headers={"User-Agent": HEADERS["User-Agent"]}, timeout=20, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
            return output_path.exists() and output_path.stat().st_size > 10000
        return False
    except Exception as e:
        print(f"[PexelsFetcher] Error descargando: {e}")
        return False
