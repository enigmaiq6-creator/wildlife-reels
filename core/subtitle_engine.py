import re
from pathlib import Path
from typing import List, Dict, Any
from config import RESOLUTIONS, SUBTITLE_CONFIG

def format_ass_time(seconds: float) -> str:
    """Converts seconds to ASS time format: H:MM:SS.cs with centisecond precision."""
    seconds = max(0.0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int(round((seconds - int(seconds)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def wrap_text_lines(text: str, max_chars_per_line: int = 30) -> str:
    """Wraps long sentences into max 2 balanced lines using \\N."""
    words = text.split()
    if len(text) <= max_chars_per_line or len(words) <= 4:
        return text

    mid = len(words) // 2
    line1 = " ".join(words[:mid])
    line2 = " ".join(words[mid:])
    return f"{line1}\\N{line2}"

class SubtitleEngine:
    def __init__(self, aspect_ratio: str = "vertical"):
        self.res = RESOLUTIONS.get(aspect_ratio, RESOLUTIONS["vertical"])
        self.width = self.res["width"]
        self.height = self.res["height"]

    def create_ass_subtitles(self, scene_data: List[Dict[str, Any]], output_ass_path: Path, total_video_duration: float = 60.0):
        """
        Generates CLASSIC DOCUMENTARY subtitles for Micro-Documentaries (Ares G style):
        - Clean, modern, high-contrast typography in safe lower-third (MarginV=480).
        - Highlights impact words ('BAM!', 'ZAS!', 'Jurassic Park') in glowing amber.
        - Frame-perfect acoustic synchronization with 35ms perceptual lead.
        """
        output_ass_path.parent.mkdir(parents=True, exist_ok=True)
        
        font_size = SUBTITLE_CONFIG.get("font_size_vertical", 46) if self.width == 1080 else 50
        margin_v = SUBTITLE_CONFIG.get("margin_v_vertical", 480) if self.width == 1080 else 120

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {self.width}
PlayResY: {self.height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: StoryDefault,Arial,{font_size},&H00FFFFFF,&H0000D4FF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,4.2,2.5,2,50,50,{margin_v},1
Style: StoryHook,Arial,{font_size + 4},&H0000FFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,40,40,{margin_v},1
Style: StoryImpact,Arial,{font_size + 10},&H0000D4FF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,110,110,0,0,1,5.5,3.0,2,40,40,{margin_v},1
Style: StoryCTA,Arial,{font_size + 2},&H0000D4FF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,4.5,2.5,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []

        for scene in scene_data:
            scene_start = scene.get("global_start", 0.0)
            scene_dur = scene.get("duration", 5.0)
            scene_end = scene_start + scene_dur
            is_hook = scene.get("is_hook", False)
            is_cta = scene.get("is_cta", False)
            is_impact = scene.get("is_impact", False)

            if is_hook:
                style_name = "StoryHook"
            elif is_cta:
                style_name = "StoryCTA"
            elif is_impact:
                style_name = "StoryImpact"
            else:
                style_name = "StoryDefault"

            word_timings = scene.get("word_timings", [])
            raw_text = scene.get("text", "").strip()

            if not word_timings:
                formatted_text = wrap_text_lines(raw_text)
                s_time = format_ass_time(scene_start)
                e_time = format_ass_time(scene_end)
                events.append(f"Dialogue: 0,{s_time},{e_time},{style_name},,0,0,0,,{{\\fad(50,50)}}{formatted_text}")
                continue

            # Natural clause grouping
            sentence_chunks = []
            current_chunk = []
            
            for w_idx, w_info in enumerate(word_timings):
                w_text = w_info["word"].strip()
                if not w_text:
                    continue
                current_chunk.append(w_info)
                
                has_strong_punct = any(p in w_text for p in [".", "!", "?", ":", ";", "—"])
                has_soft_punct = any(p in w_text for p in [",", "-"])
                
                if has_strong_punct or (has_soft_punct and len(current_chunk) >= 3) or len(current_chunk) >= 5 or w_idx == len(word_timings) - 1:
                    sentence_chunks.append(current_chunk)
                    current_chunk = []

            # Acoustic synchronization
            for idx_c, chunk in enumerate(sentence_chunks):
                chunk_raw_start = scene_start + chunk[0]["start"]
                chunk_raw_end = scene_start + chunk[-1]["end"]
                
                c_start = max(scene_start, chunk_raw_start - 0.035)
                
                if idx_c < len(sentence_chunks) - 1:
                    next_start = scene_start + sentence_chunks[idx_c + 1][0]["start"]
                    c_end = min(next_start, chunk_raw_end + 0.05)
                else:
                    c_end = min(scene_end, chunk_raw_end + 0.08)

                c_start_str = format_ass_time(c_start)
                c_end_str = format_ass_time(c_end)

                chunk_words = [w["word"] for w in chunk]
                clause_text = " ".join(chunk_words)
                
                # Check for impact words
                if any(imp in clause_text.upper() for imp in ["BAM", "ZAS", "BOOM", "CRUSH", "STRIKE"]):
                    chunk_style = "StoryImpact"
                else:
                    chunk_style = style_name

                wrapped_clause = wrap_text_lines(clause_text, max_chars_per_line=30)
                dialogue_text = f"{{\\fad(50,50)}}{wrapped_clause}"
                events.append(f"Dialogue: 0,{c_start_str},{c_end_str},{chunk_style},,0,0,0,,{dialogue_text}")

        with open(output_ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")
            
        return output_ass_path
