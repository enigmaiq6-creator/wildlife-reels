import os
import re
import random
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from config import TEMP_DIR, ASSETS_DIR

from fetchers.pexels_fetcher import search_pexels_videos, download_pexels_video
from fetchers.pixabay_fetcher import search_pixabay_videos, download_pixabay_video
from fetchers.web_social_harvester import WebSocialHarvester
from fetchers.wikimedia_fetcher import WikimediaFetcher
from fetchers.ai_motion_generator import AIMotionGenerator
from fetchers.youtube_wildlife_harvester import YouTubeWildlifeHarvester
from core.clip_validator import validate_clip_metadata

class MediaManager:
    """
    Motor Omnicanal Autónomo de Cosecha y Generación de Videos (OmniMediaEngine):
    Ejecuta una búsqueda en cascada de 6 niveles hasta obtener SIEMPRE el clip exacto del guion:
      - Nivel 1: Bóveda Curada Local (assets/clips/{creatura}/) + Auto-Cosechador Documental BBC/NatGeo
      - Nivel 2: Pexels 4K + Pixabay HD (con Validador Estricto anti-falsos positivos)
      - Nivel 3: Cosechador de Redes Sociales (Facebook Reels / Shorts con yt-dlp)
      - Nivel 4: Archivos Científicos Abiertos (Wikimedia Commons API)
      - Nivel 5: Generador Cinemático con Inteligencia Artificial (AI Motion Engine)
      - Nivel 6: Paisaje de Hábitat Natural de Respaldo Limpio
    """

    def __init__(self, temp_dir: Path = TEMP_DIR):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.used_urls = set()
        self.local_clips_dir = ASSETS_DIR / "clips"
        self.local_clips_dir.mkdir(parents=True, exist_ok=True)

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
        # NIVEL 1: BÓVEDA CURADA LOCAL + AUTO-COSECHADOR DOCUMENTAL BBC/NAT GEO
        # =====================================================================
        creature_folder = self.local_clips_dir / primary_creature
        # Si no existe la carpeta o tiene menos de 4 clips, cosechar automáticamente de documentales
        if not creature_folder.exists() or len(list(creature_folder.glob("*.mp4"))) < 4:
            YouTubeWildlifeHarvester.harvest_creature_vault(primary_creature)

        if creature_folder.exists():
            local_candidates = sorted([c for c in creature_folder.glob("*.mp4") if c.stat().st_size > 10000])
            if local_candidates:
                action_clean = action_description.lower().split("_")[0]
                matched = [c for c in local_candidates if action_clean in c.name.lower()]
                chosen = matched[0] if matched else local_candidates[(scene_id - 1) % len(local_candidates)]
                
                import shutil
                shutil.copy(chosen, output_file)
                print(f"[OmniMediaEngine] [NIVEL 1 - BÓVEDA CURADA EXACTA] Usando toma: '{chosen.name}' ({action_description})")
                return output_file

        # =====================================================================
        # NIVEL 2: PEXELS 4K + PIXABAY HD (CON VALIDADOR ESTRICTO)
        # =====================================================================
        candidates: List[Dict[str, Any]] = []

        for kw in keywords:
            print(f"[OmniMediaEngine] [NIVEL 2 - BUSCAR STOCK] Escena {scene_id} -> '{kw}'...", flush=True)
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
                print(f"  -> [NIVEL 2 - Stock Pexels 4K] {cand['title'][:55]}")
                return output_file
            elif source == "pixabay" and download_pixabay_video(url, output_file):
                print(f"  -> [NIVEL 2 - Stock Pixabay HD] {cand['title'][:55]}")
                return output_file

        # =====================================================================
        # NIVEL 3: COSECHADOR DE REDES SOCIALES (FACEBOOK / SHORTS CON YT-DLP)
        # =====================================================================
        print(f"[OmniMediaEngine] [NIVEL 3 - COSECHADOR WEB] Buscando metraje real en redes para '{subject_clean}'...")
        action_kw = keywords[0] if keywords else f"{subject_clean} wildlife"
        if WebSocialHarvester.harvest_best_clip(primary_creature, action_kw, output_file, target_duration):
            print(f"  -> [NIVEL 3 - Metraje Redes Aprobado] Clip descargado para '{subject_clean}'")
            return output_file

        # =====================================================================
        # NIVEL 4: ARCHIVOS CIENTÍFICOS ABIERTOS (WIKIMEDIA COMMONS)
        # =====================================================================
        print(f"[OmniMediaEngine] [NIVEL 4 - ARCHIVOS CIENTÍFICOS] Consultando Wikimedia Commons para '{subject_clean}'...")
        if WikimediaFetcher.search_and_download(subject_clean, action_description, output_file, target_duration):
            print(f"  -> [NIVEL 4 - Archivo Científico Descargado con Éxito]")
            return output_file

        # =====================================================================
        # NIVEL 5: GENERADOR CINEMÁTICO CON INTELIGENCIA ARTIFICIAL (AI MOTION)
        # =====================================================================
        print(f"[OmniMediaEngine] [NIVEL 5 - GENERADOR IA] Creando toma cinematográfica fotorrealista con IA...")
        if AIMotionGenerator.generate_action_clip(subject_clean, action_description, output_file, target_duration):
            print(f"  -> [NIVEL 5 - Toma Generada con IA y Animación 3D Lista]")
            return output_file

        # =====================================================================
        # NIVEL 6: PAISAJE CINEMÁTICO DEL HÁBITAT NATURAL
        # =====================================================================
        print(f"[OmniMediaEngine] [NIVEL 6 - PAISAJE HÁBITAT] Descargando entorno natural...")
        habitat_query = "deep blue ocean underwater sunlight" if "shark" in subject_clean or "orca" in subject_clean or "shrimp" in subject_clean else "amazon rainforest jungle canopy vertical"
        pex_hab = search_pexels_videos(habitat_query, orientation="portrait", max_results=4)
        for pex in pex_hab:
            url = pex.get('video_url', '')
            if url not in self.used_urls:
                self.used_urls.add(url)
                if download_pexels_video(url, output_file):
                    return output_file

        # Respaldo absoluto de emergencia con FFmpeg
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
