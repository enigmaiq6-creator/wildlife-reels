import json
import subprocess
from pathlib import Path
from typing import Optional, List
from config import TEMP_DIR, ASSETS_DIR

class YouTubeWildlifeHarvester:
    """
    Cosechador Autónomo de Metraje Documental de Alta Definición (BBC Earth / Nat Geo / Discovery).
    Busca metraje real de la criatura exacta, lo descarga y lo corta automáticamente
    en tomas verticales de acción (1080x1920) en assets/clips/{creature}/.
    """

    @classmethod
    def harvest_creature_vault(cls, creature_name: str, num_shots: int = 8) -> bool:
        clean_creature = creature_name.lower().replace("-", "_").replace(" ", "_").strip()
        target_dir = ASSETS_DIR / "clips" / clean_creature
        target_dir.mkdir(parents=True, exist_ok=True)

        # Si ya existen clips válidos en la bóveda, no es necesario volver a descargar
        existing = [c for c in target_dir.glob("*.mp4") if c.stat().st_size > 20000]
        if len(existing) >= 5:
            return True

        query_name = creature_name.lower().replace("-", " ").replace("_", " ").strip()
        search_queries = [
            f"{query_name} bbc earth 4k",
            f"{query_name} predator hunt national geographic",
            f"{query_name} wildlife documentary 4k",
            f"{query_name} wild attack slow motion"
        ]

        raw_video_path = TEMP_DIR / f"{clean_creature}_doc_raw.mp4"
        if raw_video_path.exists():
            try:
                raw_video_path.unlink()
            except Exception:
                pass

        print(f"\n[YouTubeHarvester] [🔍 BUSCANDO METRAJE DOCUMENTAL REAL] '{query_name}'...", flush=True)

        for query in search_queries:
            try:
                # 1. Buscar el video con mayor resolución en YouTube
                cmd_search = [
                    "yt-dlp",
                    f"ytsearch2:{query}",
                    "--dump-json",
                    "--no-playlist"
                ]
                res = subprocess.run(cmd_search, capture_output=True, text=True, encoding="utf-8", timeout=15)
                video_url = None
                for line in res.stdout.strip().split("\n"):
                    if line:
                        try:
                            d = json.loads(line)
                            v_id = d.get("id")
                            dur = d.get("duration", 0)
                            # Preferir videos de entre 45 segundos y 8 minutos
                            if v_id and 40 <= dur <= 600:
                                video_url = f"https://www.youtube.com/watch?v={v_id}"
                                print(f"[YouTubeHarvester] [+] Video documental encontrado: '{d.get('title')}' ({dur}s)")
                                break
                        except Exception:
                            pass

                if not video_url:
                    continue

                # 2. Descargar video con bypass de cliente Android
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
                subprocess.run(cmd_dl, timeout=40)

                if raw_video_path.exists() and raw_video_path.stat().st_size > 100000:
                    # 3. Medir duración
                    cmd_dur = [
                        "ffprobe", "-v", "error",
                        "-show_entries", "format=duration",
                        "-of", "default=noprint_wrappers=1:nokey=1",
                        str(raw_video_path)
                    ]
                    r_dur = subprocess.run(cmd_dur, capture_output=True, text=True, timeout=8)
                    total_dur = float(r_dur.stdout.strip())

                    # 4. Cortar en tomas verticales 1080x1920
                    action_labels = [
                        "01_hook_reveal",
                        "02_scale_anatomy",
                        "03_stealth_stalking",
                        "04_explosive_strike",
                        "05_death_stare_eyes",
                        "06_wild_habitat",
                        "07_climax_dramatic",
                        "08_close_up_face"
                    ]

                    step = max(2.0, (total_dur - 4.5) / max(1, num_shots))
                    extracted = 0

                    for i in range(num_shots):
                        start_t = i * step
                        label = action_labels[i % len(action_labels)]
                        out_file = target_dir / f"{label}.mp4"

                        cmd_cut = [
                            "ffmpeg", "-y",
                            "-ss", f"{start_t:.2f}",
                            "-i", str(raw_video_path),
                            "-t", "3.5",
                            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                            "-c:v", "libx264",
                            "-preset", "fast",
                            "-crf", "18",
                            "-an",
                            str(out_file)
                        ]
                        subprocess.run(cmd_cut, capture_output=True)
                        if out_file.exists() and out_file.stat().st_size > 20000:
                            extracted += 1

                    try:
                        raw_video_path.unlink()
                    except Exception:
                        pass

                    if extracted >= 4:
                        print(f"[YouTubeHarvester] [¡ÉXITO TOTAL! 🎬] {extracted} tomas de acción guardadas en: assets/clips/{clean_creature}/\n")
                        return True

            except Exception as e:
                continue

        return False
