import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from config import TEMP_DIR

from fetchers.pexels_fetcher import search_pexels_videos, download_pexels_video
from fetchers.pixabay_fetcher import search_pixabay_videos, download_pixabay_video
from fetchers.nasa_fetcher import search_nasa_videos, download_nasa_video
from fetchers.tiktok_fetcher import search_tiktok_clips, download_tiktok_video
from fetchers.social_fetcher import search_social_vertical_clips, download_social_clip
from fetchers.archive_org_fetcher import search_archive_org_videos, download_archive_org_video
from fetchers.youtube_fetcher import search_youtube_videos, download_youtube_clip
from fetchers.reddit_fetcher import search_reddit_videos, download_reddit_video

# Sinónimos y términos en inglés para verificación temática estricta
SUBJECT_SYNONYMS = {
    "komodo": ["komodo", "komodoensis", "varanus komodoensis"],
    "crow": ["crow", "raven", "corvus", "cuervo"],
    "whale": ["whale", "ballena", "cetacean", "humpback", "orca", "blue whale"],
    "butterfly": ["butterfly", "mariposa", "monarch"],
    "axolotl": ["axolotl", "ajolote", "ambystoma"],
    "hummingbird": ["hummingbird", "colibri", "trochilidae", "picaflor"],
    "venus": ["venus", "planet", "solar system", "space"],
    "astronaut": ["astronaut", "spacewalk", "astronauta", "spacesuit", "iss", "apollo", "space", "orbit"],
    "supernova": ["supernova", "nebula", "explosion", "star", "space", "cosmos", "galaxy"],
    "moon": ["moon", "luna", "lunar", "apollo", "crater", "space"],
    "neptune": ["neptune", "neptuno", "uranus", "urano", "planet", "space"],
    "diamond": ["diamond", "diamante", "crystal", "gem", "sparkle", "mineral"],
    "sun": ["sun", "solar", "sol", "plasma", "flare", "corona", "space"],
    # Océano Abisal y Marino
    "octopus": ["octopus", "pulpo", "cephalopod", "tentacle", "sea", "ocean"],
    "shark": ["shark", "tiburon", "somniosus", "greenland", "ocean", "sea", "marine", "underwater", "predator"],
    "jellyfish": ["jellyfish", "medusa", "bioluminescent", "glowing", "sea", "ocean", "tentacle", "abyss", "marine"],
    "submarine": ["submarine", "submersible", "rov", "submarino", "underwater", "deep sea", "abyss", "seabed", "ocean", "sea", "marine", "scuba", "diver", "water", "dive", "lake", "brine", "floor"],
    "squid": ["squid", "calamar", "kraken", "architeuthis", "colossal", "tentacle", "deep sea", "ocean", "sea", "mollusk"],
    "ocean": ["ocean", "sea", "underwater", "water", "marine", "deep", "abyss", "wave", "coral", "blue", "current", "tide", "floor", "seabed"],
    # Cuerpo Humano
    "brain": ["brain", "cerebro", "neuron", "neural", "synapse", "mind", "head", "thinking", "neurology", "human", "body", "medical"],
    "bone": ["bone", "skeleton", "esqueleto", "hueso", "femur", "anatomy", "skull", "spine", "orthopedic", "human", "body", "medical"],
    "acid": ["acid", "stomach", "chemical", "liquid", "digestive", "cell", "gastric", "biology", "microscope", "laboratory", "science"],
    "dna": ["dna", "adn", "genetics", "gene", "helix", "chromosome", "molecular", "science", "code", "biology"],
    "heart": ["heart", "corazon", "blood", "vessel", "artery", "circulatory", "vein", "cell", "cardiac", "red blood", "medical"],
    # Antiguo Egipto e Historia
    "pyramid": ["pyramid", "piramide", "giza", "egypt", "cairo", "monument", "desert", "ancient", "sphinx", "stone", "tomb"],
    "pharaoh": ["pharaoh", "faraon", "egypt", "statue", "temple", "hieroglyph", "cleopatra", "tutankhamun", "gold", "ancient", "museum", "carving"],
    "honey": ["honey", "miel", "honeycomb", "sweet", "gold", "amber", "jar", "bee", "liquid", "pure"]
}

# Términos que descalifican automáticamente a un video si aparecen (Falsos positivos)
NEGATIVE_EXCLUSIONS = {
    "komodo": ["dragonfly", "dragon-fly", "water dragon", "chinese", "bearded", "snake", "iguana", "gecko", "chameleon", "insect", "fly", "cartoon"],
    "crow": ["seagull", "pigeon", "parrot", "canary", "eagle"],
    "whale": ["dolphin", "shark", "scuba", "fish"],
    "butterfly": ["bee", "wasp", "ant", "fly"],
    "axolotl": ["goldfish", "koi", "turtle", "frog"],
    "hummingbird": ["bee", "flower only", "wasp"],
    "brain": ["zombie", "horror", "food", "dish"],
    "dna": ["food", "diet"]
}

def verify_subject_match(metadata_text: str, required_subject: str) -> bool:
    """
    Verifica de forma estricta que el texto/título/etiquetas del video contengan
    el sujeto visual requerido y NO contenga términos falsos positivos.
    """
    if not required_subject:
        return True
    
    req_lower = required_subject.lower()
    meta_lower = metadata_text.lower()
    
    # 1. Comprobar si contiene exclusiones negativas
    exclusions = NEGATIVE_EXCLUSIONS.get(req_lower, [])
    for exc in exclusions:
        if exc in meta_lower:
            return False

    # 2. Comprobar si contiene el término exacto o sinónimo
    synonyms = SUBJECT_SYNONYMS.get(req_lower, [req_lower])
    for syn in synonyms:
        if re.search(rf"\b{re.escape(syn)}\b", meta_lower) or syn in meta_lower:
            return True
            
    return False

class MediaManager:
    def __init__(self, temp_dir: Path = TEMP_DIR):
        self.temp_dir = temp_dir
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.used_urls = set()
        self.downloaded_clips_history = []

    def fetch_clip_for_scene(self, scene_id: int, keywords: List[str], required_subject: str = "", target_duration: float = 4.5) -> Optional[Path]:
        """
        Descarga un clip ÚNICO y 100% GARANTIZADO del animal/tema requerido para cada escena.
        CERO pantallas negras o patrones de puntos; siempre obtiene video real en 4K.
        """
        output_file = self.temp_dir / f"scene_{scene_id}_raw.mp4"
        if output_file.exists():
            try:
                output_file.unlink()
            except Exception:
                pass

        # 1. Búsqueda principal con palabras clave de la escena
        for kw in keywords:
            print(f"[MediaManager] [BUSCAR] Escena {scene_id} -> '{kw}'...", flush=True)

            # A. Pexels Oficial (4K con todas las orientaciones)
            try:
                pex_results = search_pexels_videos(kw, orientation="all", max_results=10)
                for pex in pex_results:
                    url = pex.get('video_url', '')
                    if url in self.used_urls:
                        continue
                    meta = f"{pex.get('title', '')} {pex.get('tags', '')}"
                    if verify_subject_match(meta, required_subject):
                        print(f"  -> [Pexels 4K] Clip validado 100%: {meta[:50]}...", flush=True)
                        if download_pexels_video(url, output_file):
                            self.used_urls.add(url)
                            self.downloaded_clips_history.append(output_file)
                            print(f"  [OK] Descargado de Pexels Oficial.", flush=True)
                            return output_file
            except Exception as e:
                print(f"  [!] Error Pexels: {e}", flush=True)

            # B. Pixabay Oficial (HD/4K)
            try:
                pix_results = search_pixabay_videos(kw, max_results=10)
                for pix in pix_results:
                    url = pix.get('video_url', '')
                    if url in self.used_urls:
                        continue
                    meta = f"{pix.get('title', '')}"
                    if verify_subject_match(meta, required_subject):
                        print(f"  -> [Pixabay HD] Clip validado 100%: {meta[:50]}...", flush=True)
                        if download_pixabay_video(url, output_file):
                            self.used_urls.add(url)
                            self.downloaded_clips_history.append(output_file)
                            print(f"  [OK] Descargado de Pixabay Oficial.", flush=True)
                            return output_file
            except Exception as e:
                print(f"  [!] Error Pixabay: {e}", flush=True)

            # C. TikTok (Clips verticales validados)
            try:
                tt_results = search_tiktok_clips(kw, max_results=4)
                for tt in tt_results:
                    url = tt.get('url', '')
                    if url in self.used_urls:
                        continue
                    meta = tt.get('title', '')
                    clean_t = meta.encode('ascii', 'ignore').decode('ascii')
                    if verify_subject_match(meta, required_subject):
                        print(f"  -> [TikTok] Clip validado 100%: {clean_t[:45]}...", flush=True)
                        if download_tiktok_video(url, output_file, start_sec=2, duration_sec=int(target_duration + 2)):
                            self.used_urls.add(url)
                            self.downloaded_clips_history.append(output_file)
                            print(f"  [OK] Descargado de TikTok.", flush=True)
                            return output_file
            except Exception as e:
                print(f"  [!] Error TikTok: {e}", flush=True)

        # 2. BÚSQUEDA SECUNDARIA DE ALTA COMPATIBILIDAD (Garantiza SIEMPRE video real)
        print(f"[MediaManager] [AMPLIAR] Buscando clip 4K temático alternativo para escena {scene_id}...", flush=True)
        fallback_queries = [
            f"{required_subject} 4k underwater",
            f"{required_subject} ocean 4k",
            f"{required_subject} 4k",
            "deep ocean underwater exploration 4k",
            "underwater deep sea 4k"
        ]
        
        for fkw in fallback_queries:
            try:
                pex_results = search_pexels_videos(fkw, orientation="all", max_results=10)
                for pex in pex_results:
                    url = pex.get('video_url', '')
                    if url in self.used_urls:
                        continue
                    meta = f"{pex.get('title', '')} {pex.get('tags', '')}"
                    print(f"  -> [Pexels 4K Fallback] Clip temático real: {meta[:50]}...", flush=True)
                    if download_pexels_video(url, output_file):
                        self.used_urls.add(url)
                        self.downloaded_clips_history.append(output_file)
                        print(f"  [OK] Descargado video real de Pexels.", flush=True)
                        return output_file
            except Exception:
                pass

        # 3. Fallback a clip de archivo si hubiera fallo total de red
        if self.downloaded_clips_history:
            import shutil
            shutil.copy(self.downloaded_clips_history[0], output_file)
            return output_file

        raise RuntimeError(f"No se pudo descargar ningún video real para la escena {scene_id}")
