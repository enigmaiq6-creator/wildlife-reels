import requests
from pathlib import Path
from typing import List, Optional

NASA_API_URL = "https://images-api.nasa.gov/search"

def search_nasa_videos(keyword: str, max_results: int = 3) -> List[dict]:
    """
    Busca videos oficiales de la NASA en la API pública abierta (100% Dominio Público y 4K).
    """
    params = {
        "q": keyword,
        "media_type": "video"
    }
    
    found = []
    try:
        resp = requests.get(NASA_API_URL, params=params, timeout=6)
        if resp.status_code == 200:
            items = resp.json().get("collection", {}).get("items", [])
            for item in items[:max_results]:
                data_list = item.get("data", [])
                if not data_list:
                    continue
                data = data_list[0]
                nasa_id = data.get("nasa_id", "")
                title = data.get("title", keyword)
                
                # Obtener la colección de archivos de video para este ID
                coll_url = f"https://images-api.nasa.gov/asset/{nasa_id}"
                coll_resp = requests.get(coll_url, timeout=5)
                if coll_resp.status_code == 200:
                    asset_items = coll_resp.json().get("collection", {}).get("items", [])
                    # Buscar el mejor enlace MP4 (medium o orig)
                    best_mp4 = None
                    for ai in asset_items:
                        href = ai.get("href", "")
                        if href.endswith("~medium.mp4") or href.endswith("~orig.mp4") or href.endswith(".mp4"):
                            best_mp4 = href
                            if "~medium.mp4" in href or "~orig.mp4" in href:
                                break
                    
                    if best_mp4:
                        found.append({
                            "source": "nasa",
                            "title": title,
                            "video_url": best_mp4
                        })
    except Exception as e:
        print(f"[NASAFetcher] Error buscando en NASA API: {e}")
        
    return found

def download_nasa_video(video_url: str, output_path: Path) -> bool:
    """Descarga directa del archivo MP4 de alta definición de la NASA."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(video_url, timeout=20, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=32768):
                    f.write(chunk)
            return output_path.exists() and output_path.stat().st_size > 1000
        return False
    except Exception as e:
        print(f"[NASAFetcher] Error descargando video de NASA: {e}")
        return False
