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
    print("  🦅 STARTING WILDLIFE MICRO-DOCUMENTARY ENGINE (ARES G STYLE) 🌿")
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
        # Generate fresh 6-Act Micro-Documentary via Groq AI
        topic_data = ai_gen.generate_wildlife_script(seen_topics=seen_topics)
        
        # Fallback to pre-built catalog if AI is unreachable
        if not topic_data:
            all_topics = get_all_wildlife_topics()
            available = [t for t in all_topics if t not in seen_topics]
            chosen_key = available[0] if available else all_topics[0]
            print(f"[Pipeline] [!] Using fallback catalog topic: '{chosen_key}'", flush=True)
            topic_data = WILDLIFE_CATALOG[chosen_key]

    topic_id = topic_data.get("topic_id", "WILDLIFE-DOC").lower().replace(" ", "-")
    title = topic_data.get("title", "This Creature Looks Like a Monster!")
    creature_name = topic_data.get("creature_name", topic_id.replace("-", " "))
    keywords = topic_data.get("pexels_keywords", [])
    hashtags = topic_data.get("hashtags", ["#wildlife", "#animals", "#nature", "#predators", "#shorts"])

    # Extract 6 Narrative Acts
    act1 = topic_data.get("act1_hook", "")
    act2 = topic_data.get("act2_scale", "")
    act3 = topic_data.get("act3_hunt", "")
    act4 = topic_data.get("act4_behavior", "")
    act5 = topic_data.get("act5_twist", "")
    act6 = topic_data.get("act6_climax_cta", "")

    print(f"[Pipeline] [+] Selected Creature: '{creature_name.upper()}' (Slug: {topic_id})", flush=True)
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

    raw_acts_info = [
        {"act_num": 1, "name": "Hook", "text": act1, "is_hook": True, "is_cta": False, "kw": keywords[0] if len(keywords) > 0 else f"{creature_name} 4k vertical"},
        {"act_num": 2, "name": "Monster Scale", "text": act2, "is_hook": False, "is_cta": False, "kw": keywords[1] if len(keywords) > 1 else f"{creature_name} close up head 4k"},
        {"act_num": 3, "name": "Stealth & Strike", "text": act3, "is_hook": False, "is_cta": False, "kw": keywords[2] if len(keywords) > 2 else f"{creature_name} hunting slow motion 4k"},
        {"act_num": 4, "name": "Death Stare / Trait", "text": act4, "is_hook": False, "is_cta": False, "kw": keywords[3] if len(keywords) > 3 else f"{creature_name} eyes stare camera 4k"},
        {"act_num": 5, "name": "Twist / Vulnerability", "text": act5, "is_hook": False, "is_cta": False, "kw": keywords[4] if len(keywords) > 4 else f"{creature_name} walking nature 4k vertical"},
        {"act_num": 6, "name": "Climax & CTA", "text": act6, "is_hook": False, "is_cta": True, "kw": keywords[5] if len(keywords) > 5 else f"{creature_name} mouth sound 4k"}
    ]

    # Process all 6 acts of the micro-documentary
    for idx, act in enumerate(raw_acts_info):
        act_idx = act["act_num"]
        label = act["name"]
        text = act["text"]
        kw = act["kw"]

        print(f"\n--- [Act {act_idx}/6: {label}] ---", flush=True)
        print(f"Narrative: \"{text}\"", flush=True)
        print(f"Target Camera Angle: '{kw}'", flush=True)

        # Synthesize Audio with natural pacing
        audio_data = voice_engine.synthesize_scene(text, idx)
        duration = audio_data["duration"]
        word_timings = audio_data["word_timings"]
        audio_path = audio_data["audio_path"]
        print(f"[Voice] Duration: {duration:.2f}s | Word Timings: {len(word_timings)} words", flush=True)

        # Fetch strictly matched clip for this specific creature angle
        raw_clip = media_manager.fetch_clip_for_scene(
            scene_id=idx,
            keywords=[kw, f"{creature_name} 4k vertical", f"{creature_name} wildlife 4k"],
            required_subject=creature_name.split()[0].lower(),
            target_duration=duration
        )

        # Normalize clip with Ken Burns motion
        norm_clip = TEMP_DIR / f"act_{act_idx}_norm.mp4"
        composer.process_scene_clip(raw_clip, norm_clip, duration)
        processed_clip_files.append(norm_clip)
        scene_audio_files.append(audio_path)

        scene_dict = {
            "index": idx,
            "act_num": act_idx,
            "text": text,
            "is_hook": act["is_hook"],
            "is_cta": act["is_cta"],
            "duration": duration,
            "global_start": global_time,
            "word_timings": word_timings,
            "clip_path": norm_clip,
            "audio_path": audio_path
        }
        scenes.append(scene_dict)
        global_time += duration

    total_duration = global_time
    print(f"\n[Pipeline] [+] Total Micro-Documentary Duration: {total_duration:.2f}s", flush=True)

    # 3. Concatenate video clips and audio tracks
    video_base_path = TEMP_DIR / f"wildlife_{topic_id}_base.mp4"
    audio_base_path = TEMP_DIR / f"wildlife_{topic_id}_audio.mp3"

    print("[Composer] Concatenating continuous 4K footage at constant 30 FPS...", flush=True)
    composer.concatenate_video_clips(processed_clip_files, video_base_path)

    # Whoosh SFX
    whoosh_path = SFX_DIR / "whoosh.wav"
    if not whoosh_path.exists():
        generate_cinematic_whoosh(whoosh_path)

    scene_durations = [s["duration"] for s in scenes]
    print("[Composer] Concatenating voice tracks with suspense SFX transitions...", flush=True)
    composer.concatenate_audio_tracks_with_sfx(
        scene_audio_files,
        scene_durations,
        whoosh_path,
        audio_base_path
    )

    # 4. Generate Cinematic Story Subtitles (.ass)
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ass_path = TEMP_DIR / f"subtitles_{topic_id}_{timestamp_str}.ass"
    print("[Subtitles] Burning Cinematic Story Subtitles with Frame-Perfect Acoustic Sync...", flush=True)
    subtitle_engine.create_ass_subtitles(scenes, ass_path, total_duration)

    # 5. Render Final 1080x1920 Micro-Documentary
    output_filename = f"wildlife_{topic_id}_{timestamp_str}.mp4"
    final_output_path = OUTPUT_DIR / output_filename

    # Ambient nature suspense music
    bg_music_path = MUSIC_DIR / "ambient_nature.wav"
    if not bg_music_path.exists():
        generate_ambient_cinematic_music(bg_music_path, duration=total_duration + 5.0)

    print(f"[Composer] Assembling final video -> {output_filename}...", flush=True)
    composer.build_final_video(
        video_path=video_base_path,
        voice_audio_path=audio_base_path,
        ass_subtitles_path=ass_path,
        output_final_path=final_output_path,
        total_duration=total_duration,
        bg_music_path=bg_music_path
    )
    print(f"\n[Pipeline] [MICRO-DOCUMENTARY GENERATED SUCCESSFULLY! 🎬] -> {final_output_path}", flush=True)

    # 6. Save Metadata & Description
    description = f"{title}\n\n{act1}\n\n" + "\n".join(hashtags)
    metadata_path = OUTPUT_DIR / f"metadata_{topic_id}_{timestamp_str}.txt"
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}\n\nTOPIC_ID:\n{topic_id}\n")
    print(f"[Pipeline] [+] Metadata saved to: {metadata_path.name}", flush=True)

    # 7. Meta Auto-Publish (if enabled)
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
    print(f"  🎉 MICRO-DOCUMENTARY PIPELINE COMPLETED SUCCESSFULLY")
    print(f"  Creature: {creature_name} | File: {output_filename}")
    print("=" * 65 + "\n", flush=True)
    return final_output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wildlife Micro-Documentary Engine (Ares G Style)")
    parser.add_argument("--topic", type=str, default="", help="Specific catalog topic (e.g. shoebill_stork)")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Neural voice key")
    parser.add_argument("--no-publish", action="store_true", help="Disable auto-upload to Meta")
    args = parser.parse_args()

    run_wildlife_pipeline(force_topic=args.topic, voice_key=args.voice, auto_publish=not args.no_publish)
