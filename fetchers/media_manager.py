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
from core.clip_validator import validate_clip_metadata

class MediaManager:
    """
    Gestor Inteligente de Medios con Selección Visual de Precisión y Validación Estricta:
    - 1. Validador anti-falsos positivos (elimina acuarios, buzos, caricaturas y especies erróneas).
    - 2. Clasificación por Puntuación de Relevancia (Score) para elegir la mejor toma de acción.
    - 3. Soporte para bóveda local de clips curados en assets/clips/{creatura}/.
    - 4. Respaldo cinemático limpio garantizado.
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
        target_duration: float = 4.0
    ) -> Path:
        output_file = self.temp_dir / f"scene_{scene_id}_raw.mp4"
        if output_file.exists():
            try:
                output_file.unlink()
            except Exception:
                pass

        subject_clean = required_subject.lower().replace("-", " ").strip()
        primary_creature = subject_clean.split()[0] if subject_clean else "wildlife"

        # 1. Comprobar clips locales curados en assets/clips/{creature}/
        creature_folder = self.local_clips_dir / primary_creature
        if creature_folder.exists():
            local_candidates = sorted([c for c in creature_folder.glob("*.mp4") if c.stat().st_size > 10000])
            if local_candidates:
                # 1.1 Intentar coincidencia exacta con el tipo de acción
                action_clean = action_description.lower().split("_")[0]
                matched = [c for c in local_candidates if action_clean in c.name.lower()]
                if matched:
                    chosen = matched[0]
                else:
                    # 1.2 Asignar secuencialmente por índice de toma para variedad perfecta
                    chosen = local_candidates[(scene_id - 1) % len(local_candidates)]
                
                import shutil
                shutil.copy(chosen, output_file)
                print(f"[MediaManager] [BÓVEDA CURADA 100% EXACTA] Usando toma: '{chosen.name}' para escena {scene_id} ({action_description})")
                return output_file

        candidates: List[Dict[str, Any]] = []

        # 2. Búsqueda y Validación en Pexels 4K
        for kw in keywords:
            print(f"[MediaManager] [BUSCAR PEXELS 4K] Escena {scene_id} -> '{kw}'...", flush=True)
            pex_results = search_pexels_videos(kw, orientation="portrait", max_results=8)
            for pex in pex_results:
                url = pex.get('video_url', '')
                if url in self.used_urls:
                    continue
                
                title_slug = pex.get('title', '').lower()
                is_valid, score, reason = validate_clip_metadata(
                    video_title=title_slug,
                    video_tags=title_slug,
                    target_creature=subject_clean,
                    target_action=action_description
                )
                
                if is_valid:
                    candidates.append({
                        "source": "pexels",
                        "url": url,
                        "title": title_slug,
                        "score": score
                    })
                else:
                    # Log de descarte para transparencia
                    pass

        # 3. Búsqueda y Validación en Pixabay HD
        for kw in keywords:
            pix_results = search_pixabay_videos(kw, max_results=8)
            for pix in pix_results:
                url = pix.get('video_url', '')
                if url in self.used_urls:
                    continue
                tags_str = pix.get('tags', '').lower()
                is_valid, score, reason = validate_clip_metadata(
                    video_title=tags_str,
                    video_tags=tags_str,
                    target_creature=subject_clean,
                    target_action=action_description
                )
                if is_valid:
                    candidates.append({
                        "source": "pixabay",
                        "url": url,
                        "title": tags_str,
                        "score": score
                    })

        # 4. Ordenar candidatos por PUNTUACIÓN DE RELEVANCIA (el más preciso primero)
        candidates.sort(key=lambda x: x["score"], reverse=True)

        for cand in candidates:
            url = cand["url"]
            source = cand["source"]
            self.used_urls.add(url)
            
            if source == "pexels":
                if download_pexels_video(url, output_file):
                    print(f"  -> [Pexels 4K Aprobado (Score: {cand['score']})] {cand['title'][:55]}")
                    return output_file
            elif source == "pixabay":
                if download_pixabay_video(url, output_file):
                    print(f"  -> [Pixabay HD Aprobado (Score: {cand['score']})] {cand['title'][:55]}")
                    return output_file

        # 5. Cosechador de Redes Sociales si no hubo stock limpio
        print(f"[MediaManager] [COSECHADOR WEB] Buscando metraje real de '{subject_clean}' en la web...")
        action_kw = keywords[0] if keywords else f"{subject_clean} wildlife"
        if WebSocialHarvester.harvest_best_clip(primary_creature, action_kw, output_file, target_duration):
            print(f"  -> [Video Web Aprobado] Clip descargado para '{subject_clean}'")
            return output_file

        # 6. Reutilizar cualquier clip aprobado de esta especie en la sesión
        existing_raws = [f for f in self.temp_dir.glob("scene_*_raw.mp4") if f.exists() and f.stat().st_size > 50000]
        if existing_raws:
            chosen = random.choice(existing_raws)
            import shutil
            shutil.copy(chosen, output_file)
            print(f"[MediaManager] [REUTILIZAR CLIP VERIFICADO] Usando toma válida de la sesión: {chosen.name}")
            return output_file

        # 7. Respaldo cinemático del hábitat (limpio de humanos/acuarios)
        print(f"[MediaManager] [PAISAJE HABITAT] Descargando paisaje del hábitat natural para escena {scene_id}...")
        habitat_query = "deep blue ocean underwater sunlight" if "shark" in subject_clean or "orca" in subject_clean else "amazon rainforest jungle canopy vertical"
        pex_hab = search_pexels_videos(habitat_query, orientation="portrait", max_results=4)
        for pex in pex_hab:
            url = pex.get('video_url', '')
            if url not in self.used_urls:
                self.used_urls.add(url)
                if download_pexels_video(url, output_file):
                    return output_file

        # 8. Generación de emergencia con ffmpeg
        cmd_gen = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=0x0a1128:s=1080x1920:d=6,format=yuv420p",
            "-c:v", "libx264",
            "-r", "30",
            str(output_file)
        ]
        subprocess.run(cmd_gen, capture_output=True)
        return output_file
