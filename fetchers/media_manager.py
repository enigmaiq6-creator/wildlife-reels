import os
import re
import random
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from config import TEMP_DIR, ASSETS_DIR

from fetchers.pexels_fetcher import search_pexels_videos, download_pexels_video
from fetchers.pixabay_fetcher import search_pixabay_videos, download_pixabay_video
from fetchers.web_social_harvester import WebSocialHarvester

ANIMAL_SYNONYMS = {
    "jaguar": ["jaguar", "panther", "leopard", "onca", "felid", "big cat"],
    "lion": ["lion", "lioness", "leo", "big cat"],
    "tiger": ["tiger", "tigris", "big cat"],
    "cheetah": ["cheetah", "acinonyx", "big cat"],
    "leopard": ["leopard", "panther", "big cat"],
    "orca": ["orca", "killer whale", "killer-whale", "cetacean"],
    "whale": ["whale", "humpback", "blue whale", "cetacean"],
    "shark": ["shark", "carcharodon", "great white", "hammerhead", "mako"],
    "eagle": ["eagle", "harpy", "aquila", "bird of prey", "raptor"],
    "shoebill": ["shoebill", "picozapato", "balaeniceps", "whalehead"],
    "wolf": ["wolf", "wolves", "lupus", "canis"],
    "bear": ["bear", "grizzly", "polar bear", "ursus"],
    "crocodile": ["crocodile", "alligator", "caiman", "croc", "reptile"],
    "snake": ["snake", "cobra", "viper", "python", "anaconda", "taipan", "rattlesnake"],
    "octopus": ["octopus", "cephalopod", "kraken"],
    "squid": ["squid", "calamar", "architeuthis", "cuttlefish"],
    "shrimp": ["shrimp", "mantis shrimp", "crustacean", "lobster"],
    "gecko": ["gecko", "lizard", "chameleon", "reptile"],
    "falcon": ["falcon", "peregrine", "kestrel", "raptor"]
}

def verify_title_against_subject(title_slug: str, required_subject: str) -> bool:
    """Verifica estrictamente que el clip contenga el nombre del animal requerido o sus sinónimos."""
    slug = title_slug.lower().replace("-", " ")
    subj = required_subject.lower().strip().split()[0] if required_subject else ""
    
    if not subj:
        return True

    if subj in slug:
        return True

    valid_synonyms = ANIMAL_SYNONYMS.get(subj, [subj])
    for syn in valid_synonyms:
        if syn in slug:
            return True

    return False

class MediaManager:
    """
    Gestor Inteligente Multi-Fuente con Cosechador Automático de Facebook y Pexels 4K:
    - 1. Prioriza clips locales manuales en assets/clips/ si existen.
    - 2. Búsqueda y descarga en Pexels 4K con validación biológica estricta.
    - 3. Búsqueda y descarga automática en Facebook (Facebook Reels & Videos públicos) para animales exóticos.
    - 4. Búsqueda y descarga en Pixabay HD.
    """

    def __init__(self, temp_dir: Path = TEMP_DIR):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.used_urls = set()
        self.local_clips_dir = ASSETS_DIR / "clips"
        self.local_clips_dir.mkdir(parents=True, exist_ok=True)

    def fetch_clip_for_scene(self, scene_id: int, keywords: List[str], required_subject: str = "", target_duration: float = 5.0) -> Path:
        output_file = self.temp_dir / f"scene_{scene_id}_raw.mp4"
        if output_file.exists():
            try:
                output_file.unlink()
            except Exception:
                pass

        subject_clean = required_subject.lower().replace("-", " ").strip()
        primary_animal = subject_clean.split()[0] if subject_clean else "wildlife"

        # 1. Comprobar clips locales manuales en assets/clips/
        if subject_clean:
            local_matches = list(self.local_clips_dir.glob(f"*{primary_animal}*.mp4"))
            if local_matches:
                chosen = random.choice(local_matches)
                import shutil
                shutil.copy(chosen, output_file)
                print(f"[MediaManager] [LOCAL CLIP] Usando video local exacto: {chosen.name}")
                return output_file

        # 2. Búsqueda en Pexels 4K con validación estricta de especie
        for kw in keywords:
            print(f"[MediaManager] [BUSCAR PEXELS 4K] Escena {scene_id} -> '{kw}'...", flush=True)
            pex_results = search_pexels_videos(kw, orientation="portrait", max_results=8)
            for pex in pex_results:
                url = pex.get('video_url', '')
                if url in self.used_urls:
                    continue
                
                title_slug = pex.get('title', '').lower()
                if not verify_title_against_subject(title_slug, subject_clean):
                    continue

                self.used_urls.add(url)
                if download_pexels_video(url, output_file):
                    print(f"  -> [Pexels 4K Verificado] {title_slug[:60]}")
                    return output_file

        # 3. Cosechador Automático de Facebook para animales exóticos / raros
        print(f"[MediaManager] [COSECHADOR FACEBOOK] Buscando videos reales de '{primary_animal}' en Facebook...")
        action_kw = keywords[0] if keywords else f"{primary_animal} wildlife"
        if WebSocialHarvester.harvest_best_clip(primary_animal, action_kw, output_file, target_duration):
            print(f"  -> [Facebook Video Verificado] Descargado clip real de {primary_animal}")
            return output_file

        # 4. Búsqueda en Pixabay HD con validación estricta de especie
        for kw in keywords:
            pix_results = search_pixabay_videos(kw, max_results=8)
            for pix in pix_results:
                url = pix.get('video_url', '')
                if url in self.used_urls:
                    continue
                tags_str = pix.get('tags', '').lower()
                if not verify_title_against_subject(tags_str, subject_clean):
                    continue

                self.used_urls.add(url)
                if download_pixabay_video(url, output_file):
                    print(f"  -> [Pixabay HD Verificado] {tags_str[:60]}")
                    return output_file

        # 5. Respaldo limpio del hábitat natural
        print(f"[MediaManager] [PAISAJE HABITAT] Descargando paisaje del hábitat natural para escena {scene_id}...")
        pex_hab = search_pexels_videos("wild nature landscape aerial vertical", orientation="portrait", max_results=4)
        for pex in pex_hab:
            url = pex.get('video_url', '')
            if url not in self.used_urls:
                self.used_urls.add(url)
                if download_pexels_video(url, output_file):
                    return output_file

        return output_file
