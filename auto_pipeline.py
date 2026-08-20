import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Asegurar codificación UTF-8 en consola
try:
    if sys.platform.startswith("win"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        sys.stderr.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
except Exception:
    pass

from config import (
    OUTPUT_DIR,
    TEMP_DIR,
    MUSIC_DIR,
    SFX_DIR,
    DEFAULT_VOICE,
    VIDEO_SETTINGS,
    SUBTITLE_CONFIG
)
from core.ai_script_generator import AIScriptGenerator
from core.topic_catalog import get_wildlife_topic, get_all_wildlife_topics, WILDLIFE_CATALOG
from core.voice_engine import VoiceEngine
from core.subtitle_engine import SubtitleEngine
from core.video_composer import VideoComposer
from core.audio_sfx_engine import generate_cinematic_whoosh, generate_ambient_cinematic_music
from fetchers.media_manager import MediaManager
from core.facebook_uploader import FacebookUploader
from core.instagram_uploader import InstagramUploader
from core.history_manager import HistoryManager

def run_wildlife_pipeline(force_topic: str = "", voice_key: str = DEFAULT_VOICE, auto_publish: bool = True) -> Path:
    print("\n" + "=" * 65)
    print("  🦁 STARTING WILDLIFE VIDEO ENGINE (100% SIMPLE ENGLISH) 🌿")
    print("=" * 65 + "\n", flush=True)

    history = HistoryManager(Path("history.json"))
    seen_topics = history.get_seen_topics()

    topic_data = None
    ai_gen = AIScriptGenerator()

    # 1. Script Generation / Selection
    if force_topic:
        print(f"[Pipeline] [+] Using forced catalog topic: '{force_topic}'", flush=True)
        topic_data = get_wildlife_topic(force_topic)
    else:
        # Generate fresh, unseen topic via Groq AI in Simple English
        topic_data = ai_gen.generate_wildlife_script(seen_topics=seen_topics)
        
        # Fallback to pre-built catalog if AI is unreachable
        if not topic_data:
            all_topics = get_all_wildlife_topics()
            available = [t for t in all_topics if t not in seen_topics]
            chosen_key = available[0] if available else all_topics[0]
            print(f"[Pipeline] [!] Using fallback catalog topic: '{chosen_key}'", flush=True)
            topic_data = WILDLIFE_CATALOG[chosen_key]

    topic_id = topic_data.get("topic_id", "WILDLIFE-DOC").lower().replace(" ", "-")
    title = topic_data.get("title", "5 Insane Facts About Wildlife!")
    hook = topic_data.get("hook", "")
    curiosities = topic_data.get("curiosities", [])
    cta = topic_data.get("cta", "")
    keywords = topic_data.get("pexels_keywords", [])
    hashtags = topic_data.get("hashtags", ["#wildlife", "#animals", "#nature", "#predators"])

    print(f"[Pipeline] [+] Selected Unseen Topic: '{topic_id.upper()}' (Language: SIMPLE ENGLISH)", flush=True)
    print(f"[Pipeline] [+] Title: {title}", flush=True)
    print(f"[Pipeline] [+] Voice: {voice_key}", flush=True)

    # 2. Initialize Engines
    voice_engine = VoiceEngine(voice_key=voice_key)
    media_manager = MediaManager(temp_dir=TEMP_DIR)
    subtitle_engine = SubtitleEngine(aspect_ratio="vertical")
    composer = VideoComposer(aspect_ratio="vertical")

    scenes = []
    scene_audio_files = []
    processed_clip_files = []
    global_time = 0.0

    # Build raw scene list: Hook (0), 5 Curiosities (1..5), CTA (6)
    raw_scenes_info = [
        {"scene_id": 0, "text": hook, "is_hook": True, "is_cta": False, "kw": keywords[0] if len(keywords) > 0 else f"{topic_id} animal 4k vertical"},
        {"scene_id": 1, "text": curiosities[0], "is_hook": False, "is_cta": False, "curiosity_num": 1, "kw": keywords[1] if len(keywords) > 1 else f"{topic_id} close up 4k"},
        {"scene_id": 2, "text": curiosities[1], "is_hook": False, "is_cta": False, "curiosity_num": 2, "kw": keywords[2] if len(keywords) > 2 else f"{topic_id} hunting 4k"},
        {"scene_id": 3, "text": curiosities[2], "is_hook": False, "is_cta": False, "curiosity_num": 3, "kw": keywords[3] if len(keywords) > 3 else f"{topic_id} wild action 4k"},
        {"scene_id": 4, "text": curiosities[3], "is_hook": False, "is_cta": False, "curiosity_num": 4, "kw": keywords[4] if len(keywords) > 4 else f"{topic_id} eyes 4k vertical"},
        {"scene_id": 5, "text": curiosities[4], "is_hook": False, "is_cta": False, "curiosity_num": 5, "kw": keywords[5] if len(keywords) > 5 else f"{topic_id} resting nature 4k"},
        {"scene_id": 6, "text": cta, "is_hook": False, "is_cta": True, "kw": keywords[6] if len(keywords) > 6 else "wildlife nature cinematic vertical"}
    ]

    # Generate Voice and fetch strictly matched clips for each scene
    for s_info in raw_scenes_info:
        s_id = s_info["scene_id"]
        text = s_info["text"]
        kw = s_info["kw"]
        c_num = s_info.get("curiosity_num")

        label = "Hook" if s_id == 0 else ("CTA" if s_id == 6 else f"Curiosity #{c_num}")
        print(f"\n--- [Processing Scene {s_id} / {label}] ---", flush=True)
        print(f"Text: \"{text}\"", flush=True)
        print(f"Target Keyword: '{kw}'", flush=True)

        # Synthesize Audio
        audio_data = voice_engine.synthesize_scene(text, s_id)
        duration = audio_data["duration"]
        word_timings = audio_data["word_timings"]
        audio_path = audio_data["audio_path"]
        print(f"[Voice] Duration: {duration:.2f}s | Word Timings: {len(word_timings)} words", flush=True)

        # Fetch strictly matched 4K vertical clip
        raw_clip = media_manager.fetch_clip_for_scene(
            scene_id=s_id,
            keywords=[kw, f"{topic_id} wildlife 4k vertical", "wildlife predator 4k vertical"],
            required_subject=topic_id.split("-")[0].lower(),
            target_duration=duration
        )

        # Normalize clip to exact 1080x1920 with smooth Ken Burns effect
        norm_clip = TEMP_DIR / f"scene_{s_id}_norm.mp4"
        composer.process_scene_clip(raw_clip, norm_clip, duration)
        processed_clip_files.append(norm_clip)
        scene_audio_files.append(audio_path)

        scene_dict = {
            "index": s_id,
            "scene_id": s_id,
            "text": text,
            "is_hook": s_info["is_hook"],
            "is_cta": s_info["is_cta"],
            "curiosity_index": c_num,
            "duration": duration,
            "global_start": global_time,
            "word_timings": word_timings,
            "clip_path": norm_clip,
            "audio_path": audio_path
        }
        scenes.append(scene_dict)
        global_time += duration

    total_duration = global_time
    print(f"\n[Pipeline] [+] Total Video Duration: {total_duration:.2f}s", flush=True)

    # 3. Concatenate video clips and audio tracks
    video_base_path = TEMP_DIR / f"wildlife_{topic_id}_base.mp4"
    audio_base_path = TEMP_DIR / f"wildlife_{topic_id}_audio.mp3"

    print("[Composer] Concatenating 4K video clips at constant 30 FPS...", flush=True)
    composer.concatenate_video_clips(processed_clip_files, video_base_path)

    # Generate Whoosh SFX for each curiosity transition
    whoosh_path = SFX_DIR / "whoosh.wav"
    if not whoosh_path.exists():
        generate_cinematic_whoosh(whoosh_path)

    scene_durations = [s["duration"] for s in scenes]
    print("[Composer] Concatenating audio tracks with cinematic SFX whooshes...", flush=True)
    composer.concatenate_audio_tracks_with_sfx(
        scene_audio_files,
        scene_durations,
        whoosh_path,
        audio_base_path
    )

    # 4. Generate Classic Documentary Subtitles (.ass)
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ass_path = TEMP_DIR / f"subtitles_{topic_id}_{timestamp_str}.ass"
    print("[Subtitles] Generating Classic Documentary Subtitles with Frame-Perfect Acoustic Sync...", flush=True)
    subtitle_engine.create_ass_subtitles(scenes, ass_path, total_duration)

    # 5. Render Final 1080x1920 Video with Subtitles and Music
    output_filename = f"wildlife_{topic_id}_{timestamp_str}.mp4"
    final_output_path = OUTPUT_DIR / output_filename

    # Ambient nature music
    bg_music_path = MUSIC_DIR / "ambient_nature.wav"
    if not bg_music_path.exists():
        generate_ambient_cinematic_music(bg_music_path, duration=total_duration + 5.0)

    print(f"[Composer] Burning subtitles and mixing audio into final video -> {output_filename}...", flush=True)
    composer.build_final_video(
        video_path=video_base_path,
        voice_audio_path=audio_base_path,
        ass_subtitles_path=ass_path,
        output_final_path=final_output_path,
        total_duration=total_duration,
        bg_music_path=bg_music_path
    )
    print(f"\n[Pipeline] [VIDEO GENERATED SUCCESSFULLY! 🎬] -> {final_output_path}", flush=True)

    # 6. Save Metadata
    description = f"{title} 🦁🌿\n\n{hook}\n\n" + "\n".join(hashtags)
    metadata_path = OUTPUT_DIR / f"metadata_{topic_id}_{timestamp_str}.txt"
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}\n\nTOPIC_ID:\n{topic_id}\n")
    print(f"[Pipeline] [+] Metadata saved to: {metadata_path.name}", flush=True)

    # 7. Meta Auto-Publish (if active)
    fb_post_id = ""
    if auto_publish:
        fb_uploader = FacebookUploader()
        fb_res = fb_uploader.upload_reel(final_output_path, description)
        if fb_res.get("success"):
            fb_post_id = str(fb_res.get("data", {}).get("post_id", ""))

        ig_uploader = InstagramUploader()
        ig_uploader.upload_reel_resumable(final_output_path, description)

    # Record in history
    history.record_published_topic(topic_id, title, fb_post_id)

    print("\n" + "=" * 65)
    print(f"  🎉 WILDLIFE PIPELINE COMPLETED SUCCESSFULLY")
    print(f"  Topic: {topic_id} | File: {output_filename}")
    print("=" * 65 + "\n", flush=True)
    return final_output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Simple English Wildlife Video Engine")
    parser.add_argument("--topic", type=str, default="", help="Specific catalog topic (optional)")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Neural voice key")
    parser.add_argument("--no-publish", action="store_true", help="Disable auto-upload to Meta")
    args = parser.parse_args()

    run_wildlife_pipeline(force_topic=args.topic, voice_key=args.voice, auto_publish=not args.no_publish)
