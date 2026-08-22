import urllib.request
import urllib.parse
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Dict

class WebSocialHarvester:
    """
    Cosechador Automático de Videos de Redes Sociales (Facebook Reels, TikTok, YouTube):
    - Busca videos públicos en Facebook, TikTok y YouTube usando palabras ultra-específicas.
    - Descarga el video en HD con yt-dlp directamente y sin bloqueos de sesión.
    - Control de Anti-repetición estricto por sesión.
    """

    used_urls: set = set()

    @classmethod
    def reset_session(cls):
        cls.used_urls.clear()

    @staticmethod
    def search_social_video_urls(query: str, platform: str = "facebook.com", max_results: int = 4) -> List[str]:
        """Busca URLs públicas de videos en la plataforma solicitada."""
        full_query = f"site:{platform} {query} video"
        url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(full_query)}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })

        found_links = []
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                html = r.read().decode("utf-8")
                raw_links = re.findall(r'uddg=([^&]+)', html)
                for link in raw_links:
                    unquoted = urllib.parse.unquote(link)
                    if platform in unquoted and any(p in unquoted for p in ["video", "reel", "watch", "post"]):
                        if unquoted not in found_links and unquoted not in WebSocialHarvester.used_urls:
                            found_links.append(unquoted)
                            if len(found_links) >= max_results:
                                break
        except Exception as e:
            print(f"[WebSocialHarvester] Error buscando en {platform}: {e}")

        return found_links

    @classmethod
    def harvest_best_clip(cls, animal_name: str, specific_action: str, output_path: Path, target_duration: float = 6.0) -> bool:
        """
        Busca y descarga automáticamente un clip real del animal desde Facebook o redes sociales.
        Garantiza CERO REPETICIÓN de URLs.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        search_terms = [
            f"{animal_name} {specific_action}",
            f"{animal_name} wildlife 4k",
            f"{animal_name} documentary"
        ]

        # 1. Intentar buscar en Facebook
        for term in search_terms:
            print(f"[WebSocialHarvester] Buscando video en Facebook para '{term}'...", flush=True)
            fb_urls = cls.search_social_video_urls(term, platform="facebook.com", max_results=3)
            for fb_url in fb_urls:
                if fb_url in cls.used_urls:
                    continue
                cls.used_urls.add(fb_url)
                cmd = [
                    "yt-dlp",
                    "--no-playlist",
                    "--socket-timeout", "12",
                    "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
                    "--merge-output-format", "mp4",
                    "-o", str(output_path),
                    "--force-overwrites",
                    fb_url
                ]
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
                    if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 50000:
                        print(f"[WebSocialHarvester] [¡ÉXITO TOTAL!] Video descargado de Facebook: {fb_url[:70]}")
                        return True
                except Exception as e:
                    continue

        return False
