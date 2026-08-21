import sys
import argparse
import subprocess
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent
CLIPS_DIR = BASE_DIR / "assets" / "clips"

def slice_and_import_footage(
    source_video_path: Path,
    creature_name: str,
    num_shots: int = 6,
    shot_duration: float = 3.5
) -> List[Path]:
    """
    Toma un video de vida salvaje largo o descargado y lo corta automáticamente
    en múltiples tomas de acción individuales en assets/clips/{creature}/.
    """
    clean_creature = creature_name.lower().replace("-", "_").strip()
    target_dir = CLIPS_DIR / clean_creature
    target_dir.mkdir(parents=True, exist_ok=True)

    # 1. Medir duración del video origen con ffprobe
    cmd_dur = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(source_video_path)
    ]
    try:
        res = subprocess.run(cmd_dur, capture_output=True, text=True, timeout=8)
        total_duration = float(res.stdout.strip())
    except Exception:
        total_duration = 30.0

    print(f"\n[ImportFootage] Video origen: {source_video_path.name} ({total_duration:.2f}s)")
    print(f"[ImportFootage] Extrayendo {num_shots} tomas de acción para '{clean_creature}'...")

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

    extracted_files = []
    # Calcular intervalos distribuidos a lo largo del video
    step = max(1.0, (total_duration - (shot_duration + 1.0)) / max(1, num_shots))

    for i in range(num_shots):
        start_t = i * step
        label = action_labels[i % len(action_labels)]
        out_file = target_dir / f"{label}.mp4"

        cmd_cut = [
            "ffmpeg", "-y",
            "-ss", f"{start_t:.2f}",
            "-i", str(source_video_path),
            "-t", f"{shot_duration:.2f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-an",
            str(out_file)
        ]

        res = subprocess.run(cmd_cut, capture_output=True)
        if res.returncode == 0 and out_file.exists() and out_file.stat().st_size > 10000:
            print(f"  -> [TOMA {i+1}/{num_shots}] Extraída con éxito: {out_file.name} ({start_t:.1f}s a {start_t+shot_duration:.1f}s)")
            extracted_files.append(out_file)

    print(f"[ImportFootage] [¡LISTO!] {len(extracted_files)} tomas guardadas en: {target_dir.name}/\n")
    return extracted_files

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Importador y Cortador de Metraje de Vida Salvaje")
    parser.add_argument("--source", type=str, required=True, help="Ruta al archivo de video origen")
    parser.add_argument("--creature", type=str, required=True, help="Nombre de la criatura (ej: shoebill, jaguar, shark)")
    parser.add_argument("--shots", type=int, default=6, help="Número de tomas a extraer")
    args = parser.parse_args()

    slice_and_import_footage(Path(args.source), args.creature, num_shots=args.shots)
