import re
from pathlib import Path
from typing import List, Dict, Any
from config import RESOLUTIONS, SUBTITLE_CONFIG

def format_ass_time(seconds: float) -> str:
    """Convierte segundos a formato ASS: H:MM:SS.cs con precisión de centésimas."""
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

class SubtitleEngine:
    """
    Motor de Subtítulos Virales Dinámicos (Estilo Ares G / Alex Hormozi / MrBeast):
    - Efecto Karaoke Activo: La palabra que se está pronunciando se resalta en ORO/AMARILLO NEÓN en tiempo real.
    - Sincronización Acústica Absoluta (0% desfase acumulativo).
    - Tipografía pesada (Arial Black / Bold), tamaño 64pt, contorno de 6.0px y sombra profunda.
    - Agrupación corta y dinámica (2 a 3 palabras por pantalla) en mayúsculas impactantes.
    """

    def __init__(self, aspect_ratio: str = "vertical"):
        self.res = RESOLUTIONS.get(aspect_ratio, RESOLUTIONS["vertical"])
        self.width = self.res["width"]
        self.height = self.res["height"]

    def create_ass_subtitles(self, scene_data: List[Dict[str, Any]], output_ass_path: Path, total_video_duration: float = 60.0):
        output_ass_path.parent.mkdir(parents=True, exist_ok=True)
        
        font_size = 64 if self.width == 1080 else 56
        margin_v = 470 if self.width == 1080 else 120

        # Colores en formato BGR de ASS:
        # &H0000FFFF& = Amarillo / Oro Neón Brillante (#FFFF00)
        # &H00FFFFFF& = Blanco Puro (#FFFFFF)
        # &H003B30FF& = Rojo / Ámbar de Impacto (#FF303B)
        # &H00000000& = Negro Sólido para contorno
        
        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViralText,Arial Black,{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,6.0,3.5,2,40,40,{margin_v},1
Style: ImpactText,Arial Black,{font_size + 8},&H0000D4FF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,110,110,1,0,1,7.0,4.0,2,30,30,{margin_v},1
Style: HookViralText,Arial Black,{font_size + 10},&H0000FFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,115,115,1,0,1,8.0,4.5,2,25,25,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        highlight_color = "\\c&H0000FFFF&"   # Oro Neón
        white_color = "\\c&H00FFFFFF&"       # Blanco Puro
        impact_color = "\\c&H0015D4FF&"      # Oro Brillante Intenso

        for scene in scene_data:
            scene_start = scene.get("global_start", 0.0)
            word_timings = scene.get("word_timings", [])

            if not word_timings:
                continue

            # Agrupar en fragmentos dinámicos cortos de 2 a 3 palabras
            chunks = []
            cur_chunk = []
            for w in word_timings:
                clean_w = w["word"].strip()
                if not clean_w:
                    continue
                cur_chunk.append(w)
                # Cortar si hay puntuación fuerte o llegamos a 3 palabras
                if any(p in clean_w for p in [".", "!", "?", "—", ":", ";", ","]) or len(cur_chunk) >= 3:
                    chunks.append(cur_chunk)
                    cur_chunk = []
            if cur_chunk:
                chunks.append(cur_chunk)

            # Para cada fragmento, generar eventos de Karaoke donde la palabra activa brilla
            for chunk in chunks:
                chunk_words = [w["word"].upper().strip() for w in chunk]
                
                # Duración total del bloque
                for active_idx, active_word_info in enumerate(chunk):
                    w_start = scene_start + active_word_info["start"]
                    w_end = scene_start + active_word_info["end"]
                    
                    # Evitar micro-flashes menores a 120ms para legibilidad
                    if w_end - w_start < 0.12:
                        w_end = w_start + 0.15

                    s_time_str = format_ass_time(w_start)
                    e_time_str = format_ass_time(w_end)

                    # Construir texto del chunk con la palabra activa resaltada
                    formatted_parts = []
                    is_impact_word = False

                    for idx_w, w_text in enumerate(chunk_words):
                        if idx_w == active_idx:
                            # Palabra activa resaltada
                            if any(imp in w_text for imp in ["MONSTER", "JAWS", "STRIKE", "DEATH", "PREDATOR"]):
                                is_impact_word = True
                                formatted_parts.append(f"{{{impact_color}}}{w_text}{{{white_color}}}")
                            else:
                                formatted_parts.append(f"{{{highlight_color}}}{w_text}{{{white_color}}}")
                        else:
                            # Palabra inactiva en blanco
                            formatted_parts.append(f"{{{white_color}}}{w_text}")

                    display_line = " ".join(formatted_parts)
                    if w_start <= 3.5:
                        style_to_use = "HookViralText"
                    elif is_impact_word:
                        style_to_use = "ImpactText"
                    else:
                        style_to_use = "ViralText"

                    events.append(f"Dialogue: 0,{s_time_str},{e_time_str},{style_to_use},,0,0,0,,{display_line}")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")

        print(f"[SubtitleEngine] [+] Generados {len(events)} eventos de subtítulos Karaoke 100% sincronizados.")
        return output_ass_path
