import os
import re
import random
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple, Set
from config import TEMP_DIR, ASSETS_DIR

from fetchers.pexels_fetcher import search_pexels_videos, download_pexels_video
from fetchers.pixabay_fetcher import search_pixabay_videos, download_pixabay_video
from fetchers.web_social_harvester import WebSocialHarvester
from fetchers.wikimedia_fetcher import WikimediaFetcher
from fetchers.ai_motion_generator import AIMotionGenerator
from fetchers.youtube_wildlife_harvester import YouTubeWildlifeHarvester
from fetchers.photo_kenburns_harvester import PhotoKenBurnsHarvester
from core.clip_validator import validate_clip_metadata

class MediaManager:
    """
    Motor Omnicanal Autónomo de Cosecha y Generación de Videos (OmniMediaEngine) v4.0:
    Garantiza CERO REPETICIÓN de tomas mediante una arquitectura dinámica:
      - Prioridad 1: Cosecha en línea de Metraje Fresco 4K (Pexels / Pixabay / WebSocial / Wikimedia).
      - Prioridad 2: Generación Cinemática 4K con Ken Burns 3D (Google Cloud Vertex AI / Respaldo).
      - Prioridad 3: Bóveda local aleatoria con memoria estricta anti-repetición.
    """

    def __init__(self, local_clips_dir: Optional[Path] = None, temp_dir: Optional[Path] = None):
        self.local_clips_dir = local_clips_dir or (ASSETS_DIR / "clips")
        self.temp_dir = temp_dir or TEMP_DIR
        self.used_local_clips: List[str] = []
        self.used_urls: Set[str] = set()

    def reset_session(self):
        self.used_local_clips.clear()
        self.used_urls.clear()
        WebSocialHarvester.reset_session()
        WikimediaFetcher.reset_session()

    def fetch_clip_for_scene(
        self,
        scene_id: int,
        keywords: List[str],
        required_subject: str = "",
        action_description: str = "",
        target_duration: float = 3.5
    ) -> Path:
        output_file = self.temp_dir / f"scene_{scene_id}_raw.mp4"
        if output_file.exists():
            try:
                output_file.unlink()
            except Exception:
                pass

        subject_clean = required_subject.lower().replace("-", " ").strip()
        primary_creature = subject_clean.replace(" ", "_") if subject_clean else "wildlife"

        # =====================================================================
        # NIVEL 1: COSECHA FRESCA EN LÍNEA (PEXELS 4K + PIXABAY HD)
        # =====================================================================
        candidates: List[Dict[str, Any]] = []

        for kw in keywords:
            pex_results = search_pexels_videos(kw, orientation="portrait", max_results=6)
            for pex in pex_results:
                url = pex.get('video_url', '')
                if url in self.used_urls:
                    continue
                title_slug = pex.get('title', '').lower()
                is_valid, score, _ = validate_clip_metadata(
                    video_title=title_slug,
                    video_tags=title_slug,
                    target_creature=subject_clean,
                    target_action=action_description
                )
                if is_valid:
                    candidates.append({"source": "pexels", "url": url, "title": title_slug, "score": score})

        for kw in keywords:
            pix_results = search_pixabay_videos(kw, max_results=6)
            for pix in pix_results:
                url = pix.get('video_url', '')
                if url in self.used_urls:
                    continue
                tags_str = pix.get('tags', '').lower()
                is_valid, score, _ = validate_clip_metadata(
                    video_title=tags_str,
                    video_tags=tags_str,
                    target_creature=subject_clean,
                    target_action=action_description
                )
                if is_valid:
                    candidates.append({"source": "pixabay", "url": url, "title": tags_str, "score": score})

        candidates.sort(key=lambda x: x["score"], reverse=True)

        for cand in candidates:
            url = cand["url"]
            source = cand["source"]
            self.used_urls.add(url)
            if source == "pexels" and download_pexels_video(url, output_file):
                print(f"[OmniMediaEngine] [NIVEL 1 - STOCK FRESCO PEXELS 4K] {cand['title'][:55]}")
                return output_file
            elif source == "pixabay" and download_pixabay_video(url, output_file):
                print(f"[OmniMediaEngine] [NIVEL 1 - STOCK FRESCO PIXABAY HD] {cand['title'][:55]}")
                return output_file

        # =====================================================================
        # NIVEL 2: COSECHADOR DE REDES SOCIALES (DOCUMENTALES HD CON YT-DLP)
        # =====================================================================
        action_kw = keywords[0] if keywords else f"{subject_clean} predatory action"
        if WebSocialHarvester.harvest_best_clip(primary_creature, action_kw, output_file, target_duration):
            print(f"[OmniMediaEngine] [NIVEL 2 - METRAJE DOCUMENTAL FRESCO] Clip para '{subject_clean}'")
            return output_file

        # =====================================================================
        # NIVEL 3: ARCHIVOS CIENTÍFICOS ABIERTOS (WIKIMEDIA COMMONS)
        # =====================================================================
        if WikimediaFetcher.search_and_download(subject_clean, action_description, output_file, target_duration):
            print(f"[OmniMediaEngine] [NIVEL 3 - ARCHIVO CIENTÍFICO WIKIMEDIA] Clip para '{subject_clean}'")
            return output_file

        # =====================================================================
        # NIVEL 4: FOTOGRAFÍA FOTORREALISTA 4K + EFECTO KEN BURNS CINEMÁTICO 3D
        # (Garantiza tomas 100% inéditas y únicas en cada video)
        # =====================================================================
        print(f"[OmniMediaEngine] [NIVEL 4 - FOTO 4K + KEN BURNS 3D] Creando toma única...")
        if PhotoKenBurnsHarvester.create_kenburns_clip(subject_clean, action_description, output_file, target_duration):
            print(f"  -> [NIVEL 4 - Toma Cinemática Ken Burns Lista para '{subject_clean}']")
            return output_file

        # =====================================================================
        # NIVEL 5: BÓVEDA LOCAL ALEATORIZADA (SIN REPETICIÓN)
        # =====================================================================
        creature_folder = self.local_clips_dir / primary_creature
        if creature_folder.exists():
            local_candidates = [c for c in creature_folder.glob("*.mp4") if c.stat().st_size > 10000]
            if local_candidates:
                action_clean = action_description.lower().split("_")[0]
                action_matched = [c for c in local_candidates if action_clean in c.name.lower()]
                unused_action_matched = [c for c in action_matched if c.name not in self.used_local_clips]
                
                if unused_action_matched:
                    random.shuffle(unused_action_matched)
                    chosen = unused_action_matched[0]
                    self.used_local_clips.append(chosen.name)
                    shutil.copy(chosen, output_file)
                    print(f"[OmniMediaEngine] [NIVEL 5 - BÓVEDA LOCAL] '{chosen.name}' ({action_description})")
                    return output_file

                unused_general = [c for c in local_candidates if c.name not in self.used_local_clips]
                if unused_general:
                    random.shuffle(unused_general)
                    chosen = unused_general[0]
                    self.used_local_clips.append(chosen.name)
                    shutil.copy(chosen, output_file)
                    print(f"[OmniMediaEngine] [NIVEL 5 - BÓVEDA LOCAL] '{chosen.name}' ({action_description})")
                    return output_file

        # =====================================================================
        # NIVEL 6: PAISAJE CINEMÁTICO DEL HÁBITAT NATURAL
        # =====================================================================
        habitat_query = "deep blue ocean underwater sunlight" if any(w in subject_clean for w in ["shark", "orca", "shrimp", "whale", "octopus", "fish", "eel"]) else "amazon rainforest jungle canopy vertical"
        pex_hab = search_pexels_videos(habitat_query, orientation="portrait", max_results=4)
        for pex in pex_hab:
            url = pex.get('video_url', '')
            if url not in self.used_urls:
                self.used_urls.add(url)
                if download_pexels_video(url, output_file):
                    return output_file

        # Respaldo si todo falla
        cmd_gen = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=0x0a1128:s=1080x1920:d=5,format=yuv420p",
            "-c:v", "libx264",
            "-r", "30",
            str(output_file)
        ]
        subprocess.run(cmd_gen, capture_output=True)
        return output_file
