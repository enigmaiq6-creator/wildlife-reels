import asyncio
import re
from pathlib import Path
from typing import List, Dict, Any
import edge_tts
from config import VOICES, DEFAULT_VOICE, TEMP_DIR

class VoiceEngine:
    """Neural Voice Engine in Simple English with acoustic word-level timings."""

    def __init__(self, voice_key: str = DEFAULT_VOICE):
        self.voice = VOICES.get(voice_key, VOICES["en_narrator_clear"])

    async def _generate_audio_with_timings(self, text: str, output_audio: Path) -> List[Dict[str, Any]]:
        output_audio.parent.mkdir(parents=True, exist_ok=True)
        # Clear, engaging, high-retention documentary pace
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

        # Fallback if no word boundaries emitted
        if not word_timings:
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
        """Synthesizes scene audio and returns exact duration and acoustic word timings."""
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
