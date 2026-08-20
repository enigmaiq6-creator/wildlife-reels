import requests
from pathlib import Path
from typing import List

WIKI_HEADERS = {
    "User-Agent": "CuriosityApp/1.0 (educational-video-project; contact@curiosityproject.org)"
}

def search_wikimedia_videos(keyword: str, max_results: int = 3) -> List[dict]:
    """
    Busca videos documentales, científicos o históricos en Wikimedia Commons en <1s.
    """
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": f"{keyword} filetype:video",
        "gsrnamespace": "6",
        "gsrlimit": max_results,
        "prop": "imageinfo",
        "iiprop": "url|mime|size",
        "format": "json"
    }
    
    found = []
    try:
        resp = requests.get(url, params=params, headers=WIKI_HEADERS, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            pages = data.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                title = page.get("title", "")
                infos = page.get("imageinfo", [])
                if infos:
                    info = infos[0]
                    file_url = info.get("url", "")
                    mime = info.get("mime", "")
                    
                    if "video" in mime or file_url.endswith((".webm", ".mp4", ".ogv")):
                        found.append({
                            "source": "wikimedia",
                            "title": title,
                            "video_url": file_url
                        })
    except Exception as e:
        print(f"[WikimediaFetcher] Error buscando: {e}")
        
    return found

def download_wikimedia_video(video_url: str, output_path: Path) -> bool:
    """
    Descarga archivo de video de Wikimedia Commons de alta resolución con User-Agent verificado.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(video_url, headers=WIKI_HEADERS, timeout=12, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=32768):
                    f.write(chunk)
            return output_path.exists() and output_path.stat().st_size > 1000
        return False
    except Exception as e:
        print(f"[WikimediaFetcher] Error descargando video: {e}")
        return False
