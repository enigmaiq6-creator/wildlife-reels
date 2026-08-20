import asyncio
import re
from pathlib import Path
from typing import List, Dict, Any
import edge_tts
from config import VOICES, DEFAULT_VOICE, TEMP_DIR

class VoiceEngine:
    """Motor de síntesis de voz en español con extracción de marcas acústicas temporales por frase y palabra."""

    def __init__(self, voice_key: str = DEFAULT_VOICE):
        self.voice = VOICES.get(voice_key, VOICES["es_narrator_deep"])

    async def _generate_audio_with_timings(self, text: str, output_audio: Path) -> List[Dict[str, Any]]:
        output_audio.parent.mkdir(parents=True, exist_ok=True)
        communicate = edge_tts.Communicate(text, self.voice, rate="-2%", pitch="-3Hz")
        word_timings = []
        sentence_boundaries = []

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
                elif chunk["type"] == "SentenceBoundary":
                    start_sec = chunk["offset"] / 10_000_000.0
                    dur_sec = chunk["duration"] / 10_000_000.0
                    sentence_boundaries.append({
                        "text": chunk["text"],
                        "start": start_sec,
                        "end": start_sec + dur_sec,
                        "duration": dur_sec
                    })

        # Si el motor retornó SentenceBoundary en vez de WordBoundary, calcular tiempos precisos por palabra
        if not word_timings and sentence_boundaries:
            for sb in sentence_boundaries:
                words = sb["text"].split()
                if not words:
                    continue
                total_chars = max(1, sum(len(w) for w in words))
                cur_t = sb["start"]
                for w in words:
                    w_dur = (len(w) / total_chars) * sb["duration"]
                    word_timings.append({
                        "word": w,
                        "start": cur_t,
                        "end": cur_t + w_dur
                    })
                    cur_t += w_dur
        elif not word_timings and not sentence_boundaries:
            # Fallback seguro por longitud de texto
            words = text.split()
            cur_t = 0.0
            total_chars = max(1, sum(len(w) for w in words))
            est_total_dur = max(3.0, len(text) * 0.065)
            for w in words:
                w_dur = (len(w) / total_chars) * est_total_dur
                word_timings.append({
                    "word": w,
                    "start": cur_t,
                    "end": cur_t + w_dur
                })
                cur_t += w_dur

        return word_timings

    def synthesize_scene(self, text: str, scene_idx: int) -> Dict[str, Any]:
        """Sintetiza el audio de una escena y retorna su duración exacta y marcas temporales."""
        clean_text = re.sub(r'[\*\_\"\#]', '', text).strip()
        audio_path = TEMP_DIR / f"voice_scene_{scene_idx:02d}.mp3"

        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        timings = loop.run_until_complete(
            self._generate_audio_with_timings(clean_text, audio_path)
        )

        duration = timings[-1]["end"] + 0.25 if timings else 4.0

        return {
            "text": clean_text,
            "audio_path": audio_path,
            "duration": duration,
            "word_timings": timings
        }
