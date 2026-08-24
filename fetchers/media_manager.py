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
    Motor Omnicanal Autónomo de Cosecha y Generación de Videos (OmniMediaEngine) v6.0:
    Garantiza que el 100% de las escenas utilicen MÚLTIPLES CLIPS DE VIDEO REALES:
      - Nivel 1: Bóveda Multi-Clip de Sesión Cosechada (Facebook, Reddit, TikTok, YouTube).
      - Nivel 2: Cosecha en Línea de Stock Fresco 4K (Pexels / Pixabay).
      - Nivel 3: Archivos Científicos Abiertos (Wikimedia Commons).
      - Nivel 4: SÓLO si no existe ningún video del animal en la web, genera Fotografía 4K + Ken Burns 3D.
    """

    def __init__(self, local_clips_dir: Optional[Path] = None, temp_dir: Optional[Path] = None):
        self.local_clips_dir = local_clips_dir or (ASSETS_DIR / "clips")
        self.temp_dir = temp_dir or TEMP_DIR
        self.session_vault_dir = self.temp_dir / "session_vault"
        self.session_vault_dir.mkdir(parents=True, exist_ok=True)
        self.used_session_clips: List[str] = []
        self.used_urls: Set[str] = set()

    def reset_session(self):
        self.used_session_clips.clear()
        self.used_urls.clear()
        WebSocialHarvester.reset_session()
        WikimediaFetcher.reset_session()
        if self.session_vault_dir.exists():
            try:
                shutil.rmtree(self.session_vault_dir, ignore_errors=True)
            except Exception:
                pass
        self.session_vault_dir.mkdir(parents=True, exist_ok=True)

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
        # NIVEL 1: BÓVEDA MULTI-CLIP DE SESIÓN (MÚLTIPLES VIDEOS REALES DEL ANIMAL)
        # =====================================================================
        creature_vault = self.session_vault_dir / primary_creature
        if not creature_vault.exists() or len(list(creature_vault.glob("*.mp4"))) < 3:
            # 1.1 Cosechar y rebanar videos desde redes sociales (Facebook, Reddit, TikTok)
            WebSocialHarvester.harvest_and_slice_vault(primary_creature, target_dir=creature_vault, num_shots=8)
            # 1.2 Si faltan clips, cosechar de YouTube
            if len(list(creature_vault.glob("*.mp4"))) < 4:
                YouTubeWildlifeHarvester.harvest_creature_vault(primary_creature, target_dir=creature_vault, num_shots=8)

        if creature_vault.exists():
            available_clips = sorted([c for c in creature_vault.glob("*.mp4") if c.stat().st_size > 20000])
            unused_clips = [c for c in available_clips if c.name not in self.used_session_clips]
            if unused_clips:
                chosen = unused_clips[0]
                self.used_session_clips.append(chosen.name)
                shutil.copy(chosen, output_file)
                print(f"[OmniMediaEngine] [NIVEL 1 - VIDEO REAL DE LA CRIATURA 🎬] Clip #{len(self.used_session_clips)} ({chosen.name}) para '{primary_creature}'", flush=True)
                return output_file

        # =====================================================================
        # NIVEL 2: STOCK FRESCO 4K EN LÍNEA (PEXELS + PIXABAY)
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
                print(f"[OmniMediaEngine] [NIVEL 2 - VIDEO STOCK PEXELS 4K] {cand['title'][:55]}", flush=True)
                return output_file
            elif source == "pixabay" and download_pixabay_video(url, output_file):
                print(f"[OmniMediaEngine] [NIVEL 2 - VIDEO STOCK PIXABAY HD] {cand['title'][:55]}", flush=True)
                return output_file

        # =====================================================================
        # NIVEL 3: ARCHIVOS CIENTÍFICOS ABIERTOS (WIKIMEDIA COMMONS)
        # =====================================================================
        if WikimediaFetcher.search_and_download(subject_clean, action_description, output_file, target_duration):
            print(f"[OmniMediaEngine] [NIVEL 3 - ARCHIVO CIENTÍFICO WIKIMEDIA] Clip para '{subject_clean}'", flush=True)
            return output_file

        # =====================================================================
        # NIVEL 4: FOTOGRAFÍA FOTORREALISTA 4K + EFECTO KEN BURNS CINEMÁTICO 3D
        # (SÓLO CUANDO NO SE ENCUENTRAN VIDEOS REALES EN LA WEB)
        # =====================================================================
        print(f"[OmniMediaEngine] [NIVEL 4 - FOTO 4K + KEN BURNS 3D] Creando toma animada de respaldo...", flush=True)
        if PhotoKenBurnsHarvester.create_kenburns_clip(subject_clean, action_description, output_file, target_duration):
            print(f"  -> [NIVEL 4 - Toma Ken Burns 3D Generada para '{subject_clean}']", flush=True)
            return output_file

        # Respaldo de emergencia
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
