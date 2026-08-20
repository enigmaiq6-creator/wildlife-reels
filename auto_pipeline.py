import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

from config import OUTPUT_DIR, TEMP_DIR, DEFAULT_VOICE
from core.ai_script_generator import AIScriptGenerator
from core.topic_catalog import get_wildlife_topic, get_all_wildlife_topics, WILDLIFE_CATALOG
from core.voice_engine import VoiceEngine
from core.media_downloader import MediaDownloader
from core.subtitle_engine import SubtitleEngine
from core.video_engine import VideoEngine
from core.facebook_uploader import FacebookUploader
from core.instagram_uploader import InstagramUploader
from core.history_manager import HistoryManager

def run_wildlife_pipeline(force_topic: str = "", voice_key: str = DEFAULT_VOICE, auto_publish: bool = True):
    print("=" * 65)
    print("  🦁 STARTING WILDLIFE VIDEO ENGINE (100% SIMPLE ENGLISH) 🌿")
    print("=" * 65)

    history = HistoryManager(Path("history.json"))
    seen_topics = history.get_seen_topics()

    topic_data = None
    ai_gen = AIScriptGenerator()

    # 1. Script Generation / Selection
    if force_topic:
        print(f"[Pipeline] [+] Using forced catalog topic: '{force_topic}'")
        topic_data = get_wildlife_topic(force_topic)
    else:
        # Generate fresh, unseen topic via Groq AI in Simple English
        topic_data = ai_gen.generate_wildlife_script(seen_topics=seen_topics)
        
        # Fallback to pre-built catalog if AI is unreachable
        if not topic_data:
            all_topics = get_all_wildlife_topics()
            available = [t for t in all_topics if t not in seen_topics]
            chosen_key = available[0] if available else all_topics[0]
            print(f"[Pipeline] [!] Using fallback catalog topic: '{chosen_key}'")
            topic_data = WILDLIFE_CATALOG[chosen_key]

    topic_id = topic_data.get("topic_id", "WILDLIFE-DOC").lower().replace(" ", "-")
    title = topic_data.get("title", "5 Insane Facts About Wildlife!")
    hook = topic_data.get("hook", "")
    curiosities = topic_data.get("curiosities", [])
    cta = topic_data.get("cta", "")
    keywords = topic_data.get("pexels_keywords", [])
    hashtags = topic_data.get("hashtags", ["#wildlife", "#animals", "#nature", "#predators"])

    print(f"[Pipeline] [+] Selected Unseen Topic: '{topic_id}' (Language: SIMPLE ENGLISH)")
    print(f"[Pipeline] [+] Title: {title}")
    print(f"[Pipeline] [+] Voice: {voice_key}")

    # 2. Synthesize Voice & Fetch 4K Clips
    voice = VoiceEngine(voice_key=voice_key)
    downloader = MediaDownloader()
    subtitle_engine = SubtitleEngine(aspect_ratio="vertical")
    video_engine = VideoEngine(aspect_ratio="vertical")

    scenes = []
    
    # Scene 0: Hook
    hook_kw = keywords[0] if len(keywords) > 0 else "wildlife predator 4k vertical"
    print(f"[Pipeline] [+] Processing Hook: '{hook[:50]}...'")
    hook_audio = voice.synthesize_scene(hook, 0)
    hook_clip = downloader.fetch_video_for_scene(hook_kw, 0)
    scenes.append({
        "index": 0, "text": hook, "is_hook": True, "is_cta": False,
        "audio_path": hook_audio["audio_path"], "duration": hook_audio["duration"],
        "word_timings": hook_audio["word_timings"], "clip_path": hook_clip
    })

    # Scenes 1 to 5: 5 Curiosities
    for i, cur in enumerate(curiosities, 1):
        cur_kw = keywords[i] if i < len(keywords) else "wild animal 4k vertical"
        print(f"[Pipeline] [+] Processing Curiosity #{i:02d}...")
        cur_audio = voice.synthesize_scene(cur, i)
        cur_clip = downloader.fetch_video_for_scene(cur_kw, i)
        scenes.append({
            "index": i, "curiosity_index": i, "text": cur, "is_hook": False, "is_cta": False,
            "audio_path": cur_audio["audio_path"], "duration": cur_audio["duration"],
            "word_timings": cur_audio["word_timings"], "clip_path": cur_clip
        })

    # Scene 6: Call To Action
    cta_kw = keywords[6] if len(keywords) > 6 else "african safari sunset 4k vertical"
    print(f"[Pipeline] [+] Processing CTA: '{cta[:50]}...'")
    cta_audio = voice.synthesize_scene(cta, 6)
    cta_clip = downloader.fetch_video_for_scene(cta_kw, 6)
    scenes.append({
        "index": 6, "text": cta, "is_hook": False, "is_cta": True,
        "audio_path": cta_audio["audio_path"], "duration": cta_audio["duration"],
        "word_timings": cta_audio["word_timings"], "clip_path": cta_clip
    })

    # Calculate global timeline
    current_time = 0.0
    for s in scenes:
        s["global_start"] = current_time
        current_time += s["duration"]

    total_duration = current_time
    print(f"[Pipeline] [+] Total Estimated Duration: {total_duration:.2f}s")

    # 3. Create Classic Documentary Subtitles
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ass_path = TEMP_DIR / f"subtitles_{topic_id}_{timestamp_str}.ass"
    subtitle_engine.create_ass_subtitles(scenes, ass_path, total_duration)

    # 4. Render Final Video
    output_filename = f"wildlife_{topic_id}_{timestamp_str}.mp4"
    print(f"[Pipeline] [+] Rendering 1080x1920 vertical video with FFmpeg...")
    final_video = video_engine.render_final_video(scenes, ass_path, output_filename)
    print(f"[Pipeline] [VIDEO GENERATED SUCCESSFULLY! 🎬] -> {final_video}")

    # 5. Save Simple English Metadata
    description = f"{title} 🦁🌿\n\n{hook}\n\n" + "\n".join(hashtags)
    metadata_path = OUTPUT_DIR / f"metadata_{topic_id}_{timestamp_str}.txt"
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}\n\nTOPIC_ID:\n{topic_id}\n")
    print(f"[Pipeline] [+] English metadata saved to: {metadata_path.name}")

    # 6. Meta Auto-Publish (Facebook & Instagram)
    fb_post_id = ""
    if auto_publish:
        # A. Facebook Reels
        fb_uploader = FacebookUploader()
        fb_res = fb_uploader.upload_reel(final_video, description)
        if fb_res.get("success"):
            fb_post_id = str(fb_res.get("data", {}).get("post_id", ""))

        # B. Instagram Reels (if configured)
        ig_uploader = InstagramUploader()
        ig_uploader.upload_reel_resumable(final_video, description)

    # Record in history
    history.record_published_topic(topic_id, title, fb_post_id)

    print("=" * 65)
    print(f"  🎉 WILDLIFE PIPELINE COMPLETED SUCCESSFULLY")
    print(f"  Topic: {topic_id} | File: {output_filename}")
    print("=" * 65)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Simple English Wildlife Video Engine")
    parser.add_argument("--topic", type=str, default="", help="Specific catalog topic (optional)")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Neural voice key")
    parser.add_argument("--no-publish", action="store_true", help="Disable auto-upload to Meta")
    args = parser.parse_args()

    run_wildlife_pipeline(force_topic=args.topic, voice_key=args.voice, auto_publish=not args.no_publish)
