import json
import subprocess
from pathlib import Path
from typing import Optional, List
from config import TEMP_DIR

class YouTubeWildlifeHarvester:
    """
    Cosechador Autónomo de Metraje Documental de Alta Definición (BBC Earth / Nat Geo / Discovery).
    Busca metraje REAL y LIMPIO de la criatura exacta en YouTube (B-Roll cinemático 4K).
    Filtra estrictamente para RECHAZAR:
    - Personas hablando, caras, vlogs, podcasts, entrevistas, reacciones.
    - Videos con subtítulos quemados, marcas de agua de streamers o creadores de TikTok.
    """

    BANNED_TITLE_WORDS = [
        "podcast", "reaction", "reacting", "vlog", "vlogs", "interview", "review", 
        "commentary", "talking", "storytime", "explaining", "explained", 
        "subtitles", "captions", "tiktok", "shorts", "stream", "streamer", "host", 
        "face", "person", "human", "man", "woman", "guy", "girl", "prank", "news",
        "react", "my experience", "i survived", "eating", "recipe", "cooking"
    ]

    @classmethod
    def harvest_creature_vault(cls, creature_name: str, target_dir: Optional[Path] = None, num_shots: int = 8) -> int:
        clean_creature = creature_name.lower().replace("-", "_").replace(" ", "_").strip()
        if target_dir is None:
            target_dir = TEMP_DIR / "session_vault" / clean_creature
        target_dir.mkdir(parents=True, exist_ok=True)

        existing = [c for c in target_dir.glob("*.mp4") if c.stat().st_size > 25000]
        if len(existing) >= 4:
            return len(existing)

        query_name = creature_name.lower().replace("-", " ").replace("_", " ").strip()
        search_queries = [
            f"{query_name} wildlife 4k b-roll raw footage -reaction -podcast -vlog -interview -shorts -tiktok",
            f"{query_name} bbc earth 4k -reaction -podcast -vlog -shorts -interview",
            f"{query_name} national geographic wildlife 4k -reaction -podcast -shorts",
            f"{query_name} animal in the wild 4k -vlog -podcast"
        ]

        raw_video_path = TEMP_DIR / f"{clean_creature}_doc_raw.mp4"
        if raw_video_path.exists():
            try:
                raw_video_path.unlink()
            except Exception:
                pass

        print(f"\n[YouTubeHarvester] [🔍 BUSCANDO METRAJE DOCUMENTAL LIMPIO] '{query_name}'...", flush=True)

        extracted_total = 0

        for query in search_queries:
            if extracted_total >= num_shots:
                break
            try:
                # 1. Buscar video en YouTube con yt-dlp
                cmd_search = [
                    "yt-dlp",
                    f"ytsearch5:{query}",
                    "--dump-json",
                    "--no-playlist"
                ]
                res = subprocess.run(cmd_search, capture_output=True, text=True, encoding="utf-8", timeout=18)
                video_url = None
                for line in res.stdout.strip().split("\n"):
                    if line:
                        try:
                            d = json.loads(line)
                            v_id = d.get("id")
                            v_title = d.get("title", "").lower()
                            dur = d.get("duration", 0)

                            # Filtro estricto: Descartar personas hablando, podcasts, vlogs y subtítulos
                            if any(b in v_title for b in cls.BANNED_TITLE_WORDS):
                                print(f"[YouTubeHarvester] [!] Descartado por contener persona/podcast: '{d.get('title')[:55]}'", flush=True)
                                continue

                            # Comprobar que mencione la criatura
                            creature_tokens = [w for w in query_name.split() if len(w) > 3]
                            if creature_tokens and not any(w in v_title for w in creature_tokens):
                                continue

                            if v_id and 30 <= dur <= 1200:
                                video_url = f"https://www.youtube.com/watch?v={v_id}"
                                print(f"[YouTubeHarvester] [✓] Video documental aprobado: '{d.get('title')[:60]}' ({dur}s)", flush=True)
                                break
                        except Exception:
                            pass

                if not video_url:
                    continue

                # 2. Descargar video
                cmd_dl = [
                    "yt-dlp",
                    "--extractor-args", "youtube:player_client=android",
                    "-f", "best[height<=1080]/best[height<=720]/best",
                    video_url,
                    "-o", str(raw_video_path),
                    "--no-playlist",
                    "--quiet",
                    "--no-warnings"
                ]
                subprocess.run(cmd_dl, timeout=45)

                if raw_video_path.exists() and raw_video_path.stat().st_size > 100000:
                    cmd_dur = [
                        "ffprobe", "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        str(raw_video_path)
                    ]
                    r_dur = subprocess.run(cmd_dur, capture_output=True, text=True, timeout=8)
                    total_dur = float(r_dur.stdout.strip())

                    # Extraer tomas de 3.5s de diferentes secciones evitando la intro y outro del video
                    safe_start = min(15.0, total_dur * 0.1)
                    safe_end = max(safe_start + 5.0, total_dur * 0.9)
                    usable_duration = safe_end - safe_start

                    step = max(3.5, usable_duration / max(1, num_shots))
                    
                    for i in range(num_shots):
                        start_t = safe_start + (i * step)
                        if start_t + 3.5 > safe_end:
                            break
                        out_file = target_dir / f"clip_{extracted_total + 1:02d}.mp4"
                        
                        cmd_cut = [
                            "ffmpeg", "-y",
                            "-ss", f"{start_t:.2f}",
                            "-i", str(raw_video_path),
                            "-t", "3.5",
                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                            "-c:v", "libx264",
                            "-preset", "veryfast",
                            "-crf", "20",
                            "-an",
                            str(out_file)
                        ]
                        subprocess.run(cmd_cut, capture_output=True)
                        if out_file.exists() and out_file.stat().st_size > 20000:
                            extracted_total += 1

                    try:
                        raw_video_path.unlink()
                    except Exception:
                        pass

                    if extracted_total >= 4:
                        print(f"[YouTubeHarvester] [¡ÉXITO TOTAL! 🎬] {extracted_total} tomas documentales reales extraídas para '{creature_name}'", flush=True)
                        return extracted_total

            except Exception as e:
                print(f"[YouTubeHarvester] [!] Excepción cosechando '{query}': {e}", flush=True)
                continue

        return extracted_total
