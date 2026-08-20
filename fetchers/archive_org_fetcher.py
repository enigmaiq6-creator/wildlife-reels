import requests
from pathlib import Path
from typing import List, Optional

ARCHIVE_SEARCH_URL = "https://archive.org/advancedsearch.php"

def search_archive_org_videos(keyword: str, max_results: int = 3) -> List[dict]:
    """
    Busca videos en la biblioteca de Internet Archive (Dominio Público e histórico).
    """
    params = {
        "q": f"{keyword} AND mediatype:(movies)",
        "fl[]": ["identifier", "title"],
        "rows": max_results,
        "output": "json"
    }
    
    found = []
    try:
        resp = requests.get(ARCHIVE_SEARCH_URL, params=params, timeout=5)
        if resp.status_code == 200:
            docs = resp.json().get("response", {}).get("docs", [])
            for doc in docs:
                ident = doc.get("identifier")
                title = doc.get("title", keyword)
                if ident:
                    # Consultar metadatos para obtener enlace MP4 directo
                    meta_url = f"https://archive.org/metadata/{ident}"
                    m_resp = requests.get(meta_url, timeout=4)
                    if m_resp.status_code == 200:
                        files = m_resp.json().get("files", [])
                        for f in files:
                            name = f.get("name", "")
                            fmt = f.get("format", "")
                            if fmt in ["512Kb MPEG4", "h.264", "MPEG4"] or name.endswith(".mp4"):
                                mp4_url = f"https://archive.org/download/{ident}/{name}"
                                found.append({
                                    "source": "archive_org",
                                    "title": title,
                                    "video_url": mp4_url
                                })
                                break
    except Exception as e:
        print(f"[ArchiveOrgFetcher] Error: {e}")

    return found

def download_archive_org_video(video_url: str, output_path: Path) -> bool:
    """Descarga video MP4 de Internet Archive."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        headers = {"User-Agent": "CuriosityApp/1.0 (educational)"}
        resp = requests.get(video_url, headers=headers, timeout=20, stream=True)
        if resp.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=32768):
                    f.write(chunk)
            return output_path.exists() and output_path.stat().st_size > 1000
        return False
    except Exception as e:
        print(f"[ArchiveOrgFetcher] Error descargando: {e}")
        return False
