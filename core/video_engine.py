import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any
from config import RESOLUTIONS, VIDEO_SETTINGS, TEMP_DIR, OUTPUT_DIR, MUSIC_DIR

class VideoEngine:
    """Motor de ensamblado y renderizado de video FFmpeg para Vida Salvaje."""

    def __init__(self, aspect_ratio: str = "vertical"):
        self.res = RESOLUTIONS.get(aspect_ratio, RESOLUTIONS["vertical"])
        self.width = self.res["width"]
        self.height = self.res["height"]
        self.ffmpeg = shutil.which("ffmpeg") or "ffmpeg"

    def _normalize_clip(self, input_clip: Path, output_clip: Path, duration: float) -> bool:
        """Escala y recorta el video al formato vertical 1080x1920 exacto y ajusta su duración."""
        cmd = [
            self.ffmpeg, "-y", "-stream_loop", "-1", "-i", str(input_clip),
            "-t", f"{duration:.3f}",
            "-vf", f"scale={self.width}:{self.height}:force_original_aspect_ratio=increase,crop={self.width}:{self.height},fps={VIDEO_SETTINGS['fps']}",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20", "-an",
            str(output_clip)
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0

    def render_final_video(self, scene_data: List[Dict[str, Any]], ass_subtitle_path: Path, output_filename: str) -> Path:
        """Ensambla todos los clips, audio, música de fondo y quema los subtítulos ASS."""
        concat_list_file = TEMP_DIR / "clips_concat.txt"
        normalized_clips = []

        # 1. Normalizar clips de video por cada escena
        for idx, scene in enumerate(scene_data):
            raw_clip = scene["clip_path"]
            norm_clip = TEMP_DIR / f"norm_clip_{idx:02d}.mp4"
            self._normalize_clip(raw_clip, norm_clip, scene["duration"])
            normalized_clips.append(norm_clip)

        # Crear archivo de concatenación para FFmpeg
        with open(concat_list_file, "w", encoding="utf-8") as f:
            for c in normalized_clips:
                f.write(f"file '{c.as_posix()}'\n")

        # 2. Concatenar audio de voz
        audio_concat_file = TEMP_DIR / "audio_concat.txt"
        with open(audio_concat_file, "w", encoding="utf-8") as f:
            for s in scene_data:
                f.write(f"file '{Path(s['audio_path']).as_posix()}'\n")

        full_voice_audio = TEMP_DIR / "full_voice.mp3"
        subprocess.run([
            self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(audio_concat_file),
            "-c", "copy", str(full_voice_audio)
        ], capture_output=True)

        # 3. Concatenar video base sin subtítulos
        video_base_raw = TEMP_DIR / "video_base_raw.mp4"
        subprocess.run([
            self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_file),
            "-c", "copy", str(video_base_raw)
        ], capture_output=True)

        # 4. Renderizado final con subtítulos y audio
        final_video_path = OUTPUT_DIR / output_filename
        ass_clean_path = str(ass_subtitle_path.as_posix()).replace(":", "\\:")

        # Buscar música de naturaleza si existe
        music_files = list(MUSIC_DIR.glob("*.mp3"))
        if music_files:
            bg_music = music_files[0]
            cmd = [
                self.ffmpeg, "-y",
                "-i", str(video_base_raw),
                "-i", str(full_voice_audio),
                "-stream_loop", "-1", "-i", str(bg_music),
                "-filter_complex",
                f"[0:v]subtitles='{ass_clean_path}'[v];"
                f"[1:a]volume={VIDEO_SETTINGS['voice_volume']}[a_voice];"
                f"[2:a]volume={VIDEO_SETTINGS['music_volume']}[a_music];"
                f"[a_voice][a_music]amix=inputs=2:duration=first:dropout_transition=2[a]",
                "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", VIDEO_SETTINGS["audio_bitrate"],
                "-shortest",
                str(final_video_path)
            ]
        else:
            cmd = [
                self.ffmpeg, "-y",
                "-i", str(video_base_raw),
                "-i", str(full_voice_audio),
                "-vf", f"subtitles='{ass_clean_path}'",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-c:a", "aac", "-b:a", VIDEO_SETTINGS["audio_bitrate"],
                "-shortest",
                str(final_video_path)
            ]

        subprocess.run(cmd, check=True)
        return final_video_path
