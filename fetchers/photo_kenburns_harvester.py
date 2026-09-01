import os
import sys
import json
import random
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path
from typing import Optional, List
from config import TEMP_DIR

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass
from core.clip_validator import validate_clip_metadata
from fetchers.gcp_vertex_image_generator import GCPVertexImageGenerator

class PhotoKenBurnsHarvester:
    """
    Cosechador y Generador de Fotografías de Alta Resolución con Efecto Ken Burns Cinemático.
    Cuando los clips de video se agotan o para evitar repeticiones:
      1. Genera o busca fotos en ultra alta definición con Google Cloud Vertex AI (facebookbot-502117).
      2. Aplica movimientos de cámara 3D (Zoom In a los ojos, Zoom Out revelador, Paneo anatómico).
    """

    @classmethod
    def create_kenburns_clip(
        cls,
        creature_name: str,
        action_desc: str,
        output_mp4_path: Path,
        duration: float = 3.5,
        movement_type: Optional[str] = None
    ) -> bool:
        output_mp4_path.parent.mkdir(parents=True, exist_ok=True)
        img_temp = output_mp4_path.parent / f"photo_raw_{output_mp4_path.stem}.jpg"
        if img_temp.exists():
            try:
                img_temp.unlink()
            except Exception:
                pass

        clean_creature = creature_name.lower().replace("-", " ").replace("_", " ").strip()
        clean_action = action_desc.lower().replace("_", " ").strip()

        perspectives = [
            "extreme macro close up eye stare",
            "low angle predatory full body profile",
            "lethal weapon teeth fangs claws detail",
            "stalking in natural wild habitat landscape",
            "action strike explosive motion",
            "cinematic hero lighting documentary 4k"
        ]
        chosen_persp = random.choice(perspectives)

        # 1. Intentar generar imagen de ultra alta definición con Google Cloud Vertex AI
        gcp_prompt = f"wild {clean_creature} {clean_action}, {chosen_persp}, National Geographic photography award winning 4k"
        photo_found = GCPVertexImageGenerator.generate_image(gcp_prompt, img_temp)

        # 2. Respaldo en Wikimedia Commons si fuera necesario
        if not photo_found or not img_temp.exists() or img_temp.stat().st_size < 10000:
            photo_found = cls._search_wikimedia_photo(clean_creature, f"{clean_action} {chosen_persp}", img_temp)

        # 3. Respaldo secundario
        if not photo_found or not img_temp.exists() or img_temp.stat().st_size < 10000:
            photo_found = cls._generate_ai_photo(clean_creature, f"{clean_action} {chosen_persp}", img_temp)

        if not img_temp.exists() or img_temp.stat().st_size < 8000:
            return False

        # 3. Aplicar Efecto Ken Burns con FFmpeg
        num_frames = int(duration * 30)

        motions = {
            "zoom_in": f"zoompan=z='min(zoom+0.0022,1.32)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
            "zoom_out": f"zoompan=z='max(1.32-0.0022*on,1.0)':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
            "pan_vertical": f"zoompan=z='1.22':d={num_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{num_frames})':s=1080x1920:fps=30",
            "pan_horizontal": f"zoompan=z='1.22':d={num_frames}:x='(iw-iw/zoom)*(on/{num_frames})':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30",
            "diagonal_sweep": f"zoompan=z='min(zoom+0.0015,1.25)':d={num_frames}:x='(iw-iw/zoom)*(on/{num_frames})':y='(ih-ih/zoom)*(on/{num_frames})':s=1080x1920:fps=30"
        }

        if movement_type and movement_type in motions:
            chosen_filter = motions[movement_type]
        else:
            chosen_filter = random.choice(list(motions.values()))

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_temp),
            "-t", f"{duration:.2f}",
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,{chosen_filter}[v]",
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_mp4_path)
        ]

        res = subprocess.run(cmd, capture_output=True)
        try:
            img_temp.unlink()
        except Exception:
            pass

        if res.returncode == 0 and output_mp4_path.exists() and output_mp4_path.stat().st_size > 20000:
            print(f"[KenBurnsEngine] [IMAGEN ANIMADA KEN BURNS CREADA] -> {output_mp4_path.name} ({clean_action})")
            return True

        return False

    @classmethod
    def _search_wikimedia_photo(cls, creature_name: str, action_desc: str, output_jpg: Path) -> bool:
        search_terms = [
            f"filetype:bitmap {creature_name} {action_desc}",
            f"filetype:bitmap {creature_name} close up",
            f"filetype:bitmap {creature_name} wild",
            f"filetype:bitmap {creature_name}"
        ]
        headers = {"User-Agent": "WildlifeKenBurns/2.0 (contact@wildlife.com)"}

        for q in search_terms:
            try:
                params = {
                    "action": "query",
                    "format": "json",
                    "list": "search",
                    "srnamespace": "6",
                    "srsearch": q,
                    "srlimit": "4"
                }
                url = f"https://commons.wikimedia.org/w/api.php?{urllib.parse.urlencode(params)}"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=6) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    results = data.get("query", {}).get("search", [])

                for item in results:
                    title = item.get("title", "")
                    if any(bad in title.lower() for bad in [".svg", ".png", "map", "chart", "diagram", "drawing", "illustration", "zoo"]):
                        continue

                    # Obtener URL directa
                    info_params = {
                        "action": "query",
                        "titles": title,
                        "prop": "imageinfo",
                        "iiprop": "url|mime",
                        "format": "json"
                    }
                    info_url = f"https://commons.wikimedia.org/w/api.php?{urllib.parse.urlencode(info_params)}"
                    req2 = urllib.request.Request(info_url, headers=headers)
                    with urllib.request.urlopen(req2, timeout=6) as resp2:
                        d2 = json.loads(resp2.read().decode("utf-8"))
                        pages = d2.get("query", {}).get("pages", {})
                        for pid, pdata in pages.items():
                            imginfo = pdata.get("imageinfo", [{}])[0]
                            file_url = imginfo.get("url")
                            if file_url and any(ext in file_url.lower() for ext in [".jpg", ".jpeg"]):
                                urllib.request.urlretrieve(file_url, output_jpg)
                                if output_jpg.exists() and output_jpg.stat().st_size > 30000:
                                    print(f"[KenBurnsEngine] [+] Fotografía real descargada: '{title[:45]}'")
                                    return True
            except Exception:
                continue

        return False

    @classmethod
    def _generate_ai_photo(cls, creature_name: str, action_desc: str, output_jpg: Path) -> bool:
        prompts = [
            f"National Geographic award winning photorealistic vertical portrait of {creature_name} {action_desc}, 4k ultra detailed wildlife photography, cinematic natural light",
            f"Hyperrealistic 4k vertical macro close-up of {creature_name} in wild nature, BBC Earth documentary photo, ultra sharp focus, 8k resolution"
        ]
        chosen_prompt = random.choice(prompts)
        seed = random.randint(1000, 999999)

        try:
            encoded_prompt = urllib.parse.quote(chosen_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={seed}&model=turbo"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = resp.read()
                if len(data) > 10000:
                    output_jpg.write_bytes(data)
                    return True
        except Exception:
            pass

        return False
