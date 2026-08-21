import random
import urllib.request
import urllib.parse
import subprocess
from pathlib import Path

class AIMotionGenerator:
    """
    Generador Cinemático por Inteligencia Artificial (Nivel 5 de Respaldo Absoluto):
    - Genera visuales fotorrealistas en 4K estilo National Geographic para tomas raras o extremas.
    - Aplica un motor de animación de cámara cinemática 3D (Ken Burns, zoom progresivo y paneo de cine).
    - Garantiza que NUNCA exista un video con pantallas negras ni errores de metraje.
    """

    @classmethod
    def generate_action_clip(
        cls,
        creature_name: str,
        action_desc: str,
        output_path: Path,
        duration: float = 3.5
    ) -> bool:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img_temp = output_path.parent / f"ai_raw_{output_path.stem}.jpg"

        # 1. Construir prompt hiperrealista para documental de naturaleza
        clean_creature = creature_name.lower().replace("-", " ").strip()
        action_clean = action_desc.lower().replace("_", " ").strip()

        cinematic_prompts = [
            f"Award winning photorealistic 4k vertical national geographic shot of wild {clean_creature} {action_clean}, natural wildlife photography, detailed cinematic lighting, ultra sharp focus, 8k resolution",
            f"Extremely detailed vertical 4k close up of {clean_creature} {action_clean}, BBC Earth documentary style, realistic textures, volumetric natural light",
            f"Cinematic action photo vertical of {clean_creature} in wild habitat, intense predator gaze, award winning nature photography 4k"
        ]
        chosen_prompt = random.choice(cinematic_prompts)
        seed = random.randint(1000, 999999)

        print(f"[AIMotionGenerator] [🎨 GENERANDO TOMA IA] '{clean_creature}' -> {action_clean}...")

        # 2. Descargar imagen fotorrealista desde endpoint de ultra velocidad
        try:
            encoded_prompt = urllib.parse.quote(chosen_prompt)
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1920&nologo=true&seed={seed}&model=turbo"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = resp.read()
                if len(data) > 10000:
                    img_temp.write_bytes(data)
        except Exception as e:
            print(f"[AIMotionGenerator] [!] Error descargando visual IA: {e}")
            return False

        if not img_temp.exists() or img_temp.stat().st_size < 10000:
            return False

        # 3. Animar con Cámara Cinemática 3D (Ken Burns + Paneo progresivo a 30 FPS constantes)
        zoom_modes = [
            "min(zoom+0.0018,1.25)",      # Acercamiento lento a los ojos
            "max(1.25-0.0018*on,1.0)",     # Alejamiento revelador
            "min(zoom+0.0012,1.18)"       # Paneo sutil
        ]
        chosen_zoom = random.choice(zoom_modes)
        num_frames = int(duration * 30)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_temp),
            "-t", f"{duration:.2f}",
            "-filter_complex",
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='{chosen_zoom}':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30[v]",
            "-map", "[v]",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-pix_fmt", "yuv420p",
            "-an",
            str(output_path)
        ]

        res = subprocess.run(cmd, capture_output=True)
        try:
            img_temp.unlink()
        except Exception:
            pass

        if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 20000:
            print(f"[AIMotionGenerator] [¡TOMA IA GENERADA CON ÉXITO! ✨] -> {output_path.name}")
            return True

        return False
