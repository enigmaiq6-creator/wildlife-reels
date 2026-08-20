import os
import random
import urllib.request
import urllib.parse
import json
from pathlib import Path
from typing import List, Optional
from config import TEMP_DIR

class MediaDownloader:
    """Descargador de clips de video de fauna y naturaleza en alta definición (Pexels y Pixabay)."""

    def __init__(self, pexels_key: Optional[str] = None, pixabay_key: Optional[str] = None):
        self.pexels_key = pexels_key or os.getenv("PEXELS_API_KEY", "")
        self.pixabay_key = pixabay_key or os.getenv("PIXABAY_API_KEY", "")

    def _download_pexels_video(self, query: str, output_path: Path) -> bool:
        if not self.pexels_key:
            return False

        try:
            url = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&orientation=portrait&per_page=12"
            req = urllib.request.Request(url, headers={"Authorization": self.pexels_key, "User-Agent": "WildlifeVideoEngine/2.0"})
            
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
                videos = data.get("videos", [])
                if not videos:
                    # Intentar búsqueda general sin filtro vertical estricto
                    url_general = f"https://api.pexels.com/videos/search?query={urllib.parse.quote(query)}&per_page=8"
                    req_gen = urllib.request.Request(url_general, headers={"Authorization": self.pexels_key})
                    with urllib.request.urlopen(req_gen, timeout=10) as r_gen:
                        videos = json.loads(r_gen.read().decode("utf-8")).get("videos", [])

                if videos:
                    selected_video = random.choice(videos[:4])
                    video_files = selected_video.get("video_files", [])
                    # Priorizar calidad HD/4K vertical
                    video_files.sort(key=lambda x: (x.get("width", 0) * x.get("height", 0)), reverse=True)
                    target_file = video_files[0] if video_files else None

                    if target_file and "link" in target_file:
                        urllib.request.urlretrieve(target_file["link"], str(output_path))
                        return True
        except Exception as e:
            print(f"[MediaDownloader] [!] Error buscando en Pexels ('{query}'): {e}")

        return False

    def _download_pixabay_video(self, query: str, output_path: Path) -> bool:
        if not self.pixabay_key:
            return False

        try:
            url = f"https://pixabay.com/api/videos/?key={self.pixabay_key}&q={urllib.parse.quote(query)}&video_type=film&per_page=8"
            req = urllib.request.Request(url, headers={"User-Agent": "WildlifeVideoEngine/2.0"})
            with urllib.request.urlopen(req, timeout=12) as response:
                data = json.loads(response.read().decode("utf-8"))
                hits = data.get("hits", [])
                if hits:
                    hit = random.choice(hits[:3])
                    v_videos = hit.get("videos", {})
                    for size in ["large", "medium", "small"]:
                        if size in v_videos and "url" in v_videos[size]:
                            v_url = v_videos[size]["url"]
                            if v_url:
                                urllib.request.urlretrieve(v_url, str(output_path))
                                return True
        except Exception as e:
            print(f"[MediaDownloader] [!] Error buscando en Pixabay ('{query}'): {e}")

        return False

    def fetch_video_for_scene(self, query: str, scene_idx: int) -> Path:
        """Descarga el mejor clip disponible para una escena o genera un fondo cinemático de respaldo."""
        output_file = TEMP_DIR / f"clip_scene_{scene_idx:02d}.mp4"
        
        # 1. Intentar Pexels
        if self._download_pexels_video(query, output_file):
            return output_file

        # 2. Intentar Pixabay
        if self._download_pixabay_video(query, output_file):
            return output_file

        # 3. Respaldo temático de naturaleza
        fallback_query = "wildlife nature cinematic"
        if self._download_pexels_video(fallback_query, output_file):
            return output_file

        return output_file
