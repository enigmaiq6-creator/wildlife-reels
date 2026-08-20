import asyncio
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any
import edge_tts
from config import VOICES, DEFAULT_VOICE, TEMP_DIR

def get_exact_audio_duration(audio_file: Path) -> float:
    """Extrae la duración física exacta en microsegundos usando ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(audio_file)
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        if res.returncode == 0 and res.stdout.strip():
            return float(res.stdout.strip())
    except Exception as e:
        print(f"[VoiceEngine] Error en ffprobe: {e}")
    return 4.0

class VoiceEngine:
    """Motor de Voz Neuronal con extracción acústica milimétrica y validación física ffprobe."""

    def __init__(self, voice_key: str = DEFAULT_VOICE):
        self.voice = VOICES.get(voice_key, VOICES["en_narrator_clear"])

    async def _generate_audio_with_timings(self, text: str, output_audio: Path) -> List[Dict[str, Any]]:
        output_audio.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text, self.voice, rate="+0%", pitch="-1Hz")
        word_timings = []

        with open(output_audio, "wb") as f:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    start_sec = chunk["offset"] / 10_000_000.0
                    dur_sec = chunk["duration"] / 10_000_000.0
                    word_timings.append({
                        "word": chunk["text"],
                        "start": start_sec,
                        "end": start_sec + dur_sec
                    })

        # Medir duración física real del archivo mp3 generado
        exact_duration = get_exact_audio_duration(output_audio)

        # Si no hubo eventos de WordBoundary, interpolar proporcionalmente
        if not word_timings:
            words = text.split()
            cur_t = 0.0
            total_chars = max(1, sum(len(w) for w in words))
            for w in words:
                w_dur = (len(w) / total_chars) * (exact_duration - 0.1)
                word_timings.append({
                    "word": w,
                    "start": cur_t,
                    "end": cur_t + w_dur
                })
                cur_t += w_dur

        return word_timings, exact_duration

    def synthesize_scene(self, text: str, scene_idx: int) -> Dict[str, Any]:
        """Sintetiza audio y retorna la duración física exacta y tiempos de cada palabra."""
        clean_text = re.sub(r'[\*\_\"\#]', '', text).strip()
        audio_path = TEMP_DIR / f"voice_scene_{scene_idx:02d}.mp3"

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        timings, physical_duration = loop.run_until_complete(
            self._generate_audio_with_timings(clean_text, audio_path)
        )

        return {
            "text": clean_text,
            "audio_path": audio_path,
            "duration": physical_duration,
            "word_timings": timings
        }
