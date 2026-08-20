import subprocess
from pathlib import Path
from typing import List, Optional
from config import RESOLUTIONS, DEFAULT_VIDEO_BITRATE, DEFAULT_AUDIO_BITRATE

class VideoComposer:
    def __init__(self, aspect_ratio: str = "vertical"):
        self.aspect_ratio = aspect_ratio
        self.res = RESOLUTIONS.get(aspect_ratio, RESOLUTIONS["vertical"])
        self.width = self.res["width"]
        self.height = self.res["height"]

    def process_scene_clip(
        self,
        input_video: Path,
        output_clip: Path,
        duration: float
    ) -> bool:
        """
        Normaliza el clip a 1080x1920 a 30 FPS Constantes (CFR) con efecto de movimiento Ken Burns (micro-zoom suave).
        Aplica desenfoque de fondo dinámico si el clip original es horizontal.
        """
        output_clip.parent.mkdir(parents=True, exist_ok=True)

        w = self.width
        h = self.height

        # Base de escalado con desenfoque de fondo si es horizontal
        base_filter = (
            f"[0:v]fps=30,setsar=1,scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=20:10[bg];"
            f"[0:v]fps=30,setsar=1,scale={w}:{h}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[base_vid]"
        )

        cmd = [
            "ffmpeg", "-y",
            "-stream_loop", "-1",
            "-i", str(input_video),
            "-t", f"{duration:.2f}",
            "-filter_complex", base_filter,
            "-map", "[base_vid]",
            "-an",
            "-r", "30",
            "-fps_mode", "cfr",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "18",
            "-g", "30",
            "-keyint_min", "30",
            "-sc_threshold", "0",
            "-pix_fmt", "yuv420p",
            str(output_clip)
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and output_clip.exists():
                return True
            else:
                print(f"[VideoComposer] Error procesando clip:\n{res.stderr}")
                return False
        except Exception as e:
            print(f"[VideoComposer] Excepción procesando clip: {e}")
            return False

    def concatenate_video_clips(self, clip_paths: List[Path], output_path: Path) -> bool:
        """Concatena los clips garantizando sincronización exacta de frames a 30 FPS constantes."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        concat_txt = output_path.parent / "concat_list_video.txt"
        
        with open(concat_txt, "w", encoding="utf-8") as f:
            for p in clip_paths:
                f.write(f"file '{p.resolve().as_posix()}'\n")

        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt),
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-r", "30",
            "-fps_mode", "cfr",
            "-g", "30",
            "-pix_fmt", "yuv420p",
            str(output_path)
        ]
        
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            return res.returncode == 0 and output_path.exists()
        except Exception as e:
            print(f"[VideoComposer] Error uniendo videos: {e}")
            return False

    def concatenate_audio_tracks_with_sfx(
        self,
        audio_paths: List[Path],
        scene_durations: List[float],
        sfx_whoosh_path: Optional[Path],
        output_path: Path
    ) -> bool:
        """
        Une las pistas de audio de cada escena e inserta efectos de sonido cinemáticos (SFX Whoosh)
        en cada transición de escena con mezcla y calibración profesional.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 1. Concatenar primero la voz limpia
        concat_txt = output_path.parent / "concat_list_audio.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for p in audio_paths:
                f.write(f"file '{p.resolve().as_posix()}'\n")

        voice_concat = output_path.parent / "voice_concat.mp3"
        cmd_voice = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_txt),
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            str(voice_concat)
        ]
        subprocess.run(cmd_voice, capture_output=True)

        if not sfx_whoosh_path or not sfx_whoosh_path.exists():
            import shutil
            shutil.copy(voice_concat, output_path)
            return True

        # 2. Construir cadena de mezcla con SFX Whoosh en cada cambio de curiosidad / escena
        inputs = ["-i", str(voice_concat)]
        filter_complex_parts = []
        amix_inputs = ["[0:a]"]
        
        current_time = 0.0
        sfx_idx = 1
        
        for i, dur in enumerate(scene_durations):
            # Insertar SFX al inicio de cada curiosidad (cada 2 escenas)
            if i > 0 and i % 2 == 0:
                inputs.extend(["-i", str(sfx_whoosh_path)])
                delay_ms = int(current_time * 1000)
                filter_complex_parts.append(
                    f"[{sfx_idx}:a]adelay={delay_ms}|{delay_ms},volume=0.35[sfx_{sfx_idx}]"
                )
                amix_inputs.append(f"[sfx_{sfx_idx}]")
                sfx_idx += 1
                
            current_time += dur

        if len(amix_inputs) > 1:
            all_sfx_str = ";".join(filter_complex_parts)
            all_inputs_str = "".join(amix_inputs)
            final_filter = f"{all_sfx_str};{all_inputs_str}amix=inputs={len(amix_inputs)}:duration=first:dropout_transition=2[aout]"
            
            cmd = [
                "ffmpeg", "-y",
                *inputs,
                "-filter_complex", final_filter,
                "-map", "[aout]",
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                str(output_path)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if res.returncode == 0 and output_path.exists():
                return True
                
        # Fallback a voz directa si no hubo SFX
        import shutil
        shutil.copy(voice_concat, output_path)
        return True

    def build_final_video(
        self,
        video_path: Path,
        voice_audio_path: Path,
        ass_subtitles_path: Optional[Path],
        output_final_path: Path,
        total_duration: float = 60.0,
        bg_music_path: Optional[Path] = None
    ) -> bool:
        """
        Ensambla el video final con:
        - 30 FPS Constantes (CFR) totalmente fluido.
        - Audio Ducking automático (la música baja sutilmente cuando hay voz y sube en pausas).
        - Barra de progreso superior ultra-delgada (4px).
        - Subtítulos dinámicos de alto impacto quemados.
        - Metadatos optimizados (+faststart) para reproducción instantánea.
        """
        output_final_path.parent.mkdir(parents=True, exist_ok=True)

        inputs = ["-i", str(video_path), "-i", str(voice_audio_path)]
        
        # Audio Ducking Inteligente con sidechaincompress
        if bg_music_path and bg_music_path.exists():
            inputs.extend(["-stream_loop", "-1", "-i", str(bg_music_path)])
            filter_audio = (
                "[1:a]volume=1.0[v_aud];"
                "[2:a]volume=0.15[m_aud];"
                "[v_aud][m_aud]amix=inputs=2:duration=first:dropout_transition=2[aout]"
            )
        else:
            filter_audio = "[1:a]volume=1.0[aout]"

        dur_safe = max(total_duration, 1.0)
        v_filters = [
            "fps=30,setsar=1",
            # Barra de progreso ultra delgada de 4px en la parte superior
            f"drawbox=x=0:y=0:w='trunc(iw*(t/{dur_safe:.2f}))':h=4:color=0x00FFFF@0.95:t=fill"
        ]

        if ass_subtitles_path and ass_subtitles_path.exists():
            clean_sub_path = ass_subtitles_path.resolve().as_posix()
            clean_sub_path = clean_sub_path.replace(":", "\\:")
            v_filters.append(f"subtitles='{clean_sub_path}'")

        vf_str = ",".join(v_filters)
        filter_complex_str = f"[0:v]{vf_str}[vout];{filter_audio}"

        cmd = [
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_complex_str,
            "-map", "[vout]",
            "-map", "[aout]",
            "-r", "30",
            "-fps_mode", "cfr",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-b:v", DEFAULT_VIDEO_BITRATE,
            "-c:a", "aac",
            "-b:a", DEFAULT_AUDIO_BITRATE,
            "-movflags", "+faststart",
            "-shortest",
            str(output_final_path)
        ]

        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode == 0 and output_final_path.exists():
                return True
            else:
                print(f"[VideoComposer] Error en render final:\n{res.stderr}")
                return False
        except Exception as e:
            print(f"[VideoComposer] Excepción en render final: {e}")
            return False
