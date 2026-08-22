import json
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any
from core.clip_validator import validate_clip_metadata

class WikimediaFetcher:
    """
    Cosechador de Archivos Científicos y Biológicos Abiertos de Wikimedia Commons.
    Descarga metraje real de acceso libre categorizado por taxonomía biológica.
    Control de Anti-repetición estricto por sesión.
    """

    BASE_API = "https://commons.wikimedia.org/w/api.php"
    HEADERS = {"User-Agent": "WildlifeOmniEngine/2.0 (contact@wildlife.com)"}
    used_urls: set = set()

    @classmethod
    def reset_session(cls):
        cls.used_urls.clear()

    @classmethod
    def search_and_download(
        cls,
        creature_name: str,
        action_desc: str,
        output_path: Path,
        target_duration: float = 3.5
    ) -> bool:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        search_terms = [
            f"filetype:video {creature_name}",
            f"filetype:video {creature_name} hunting",
            f"filetype:video {creature_name} wild"
        ]

        for query in search_terms:
            try:
                params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srnamespace": "6", # Namespace 6 = File
                    "srsearch": query,
                    "srlimit": "6"
                }
                req_url = f"{cls.BASE_API}?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(req_url, headers=cls.HEADERS)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    results = data.get("query", {}).get("search", [])

                for item in results:
                    title = item.get("title", "")
                    # Validar metadatos y rechazar dibujos / caricaturas / especies equivocadas
                    is_valid, score, reason = validate_clip_metadata(
                        video_title=title,
                        video_tags=title,
                        target_creature=creature_name,
                        target_action=action_desc
                    )

                    if not is_valid:
                        continue

                    # Obtener URL directa del archivo multimedia
                    info_params = {
                        "action": "query",
                        "titles": title,
                        "prop": "imageinfo",
                        "iiprop": "url|mime",
                        "format": "json"
                    }
                    info_url = f"{cls.BASE_API}?{urllib.parse.urlencode(info_params)}"
                    req2 = urllib.request.Request(info_url, headers=cls.HEADERS)
                    with urllib.request.urlopen(req2, timeout=8) as resp2:
                        d2 = json.loads(resp2.read().decode("utf-8"))
                        pages = d2.get("query", {}).get("pages", {})
                        for pid, pdata in pages.items():
                            imginfo = pdata.get("imageinfo", [{}])[0]
                            file_direct_url = imginfo.get("url")
                            if file_direct_url and file_direct_url not in cls.used_urls:
                                cls.used_urls.add(file_direct_url)
                                print(f"[WikimediaFetcher] [+] Descargando archivo científico único: {title[:50]}...")
                                temp_dl = output_path.parent / f"wiki_temp_{output_path.stem}.webm"
                                urllib.request.urlretrieve(file_direct_url, temp_dl)
                                if temp_dl.exists() and temp_dl.stat().st_size > 15000:
                                    # Convertir a 1080x1920 vertical H.264
                                    cmd = [
                                        "ffmpeg", "-y",
                                        "-i", str(temp_dl),
                                        "-t", f"{target_duration:.2f}",
                                        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                                        "-c:v", "libx264",
                                        "-preset", "fast",
                                        "-pix_fmt", "yuv420p",
                                        "-an",
                                        str(output_path)
                                    ]
                                    subprocess.run(cmd, capture_output=True)
                                    try:
                                        temp_dl.unlink()
                                    except Exception:
                                        pass
                                    if output_path.exists() and output_path.stat().st_size > 20000:
                                        print(f"[WikimediaFetcher] [¡ÉXITO!] Video científico procesado: {output_path.name}")
                                        return True
            except Exception as e:
                continue

        return False
