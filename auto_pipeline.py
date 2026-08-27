import os
import sys
import random
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
    SUBTITLE_CONFIG,
    PACING_SETTINGS
)
from core.ai_script_generator import AIScriptGenerator
from core.topic_catalog import get_wildlife_topic, get_all_wildlife_topics, WILDLIFE_CATALOG
from core.top_catalog import get_top_topic, get_all_top_topics, TOP_CATALOG
from core.ai_top_generator import AITopGenerator
from core.voice_engine import VoiceEngine
from core.subtitle_engine import SubtitleEngine
from core.video_composer import VideoComposer
from core.audio_sfx_engine import generate_cinematic_whoosh, generate_ambient_cinematic_music
from fetchers.media_manager import MediaManager
from publisher.facebook_publisher import FacebookPublisher
from core.history_manager import HistoryManager

# =====================================================================
#  MODO 1: MICRO-DOCUMENTAL DE CRIATURA ÚNICA (ARES G STYLE)
# =====================================================================
def run_single_creature_pipeline(force_topic: str = "", voice_key: str = DEFAULT_VOICE, auto_publish: bool = True) -> Path:
    print("\n" + "=" * 65)
    print("  🦅 MODO 1: MICRO-DOCUMENTAL DE CRIATURA ÚNICA (ARES G STYLE) 🌿")
    print("=" * 65 + "\n", flush=True)

    history = HistoryManager(Path("history.json"))
    seen_topics = history.get_seen_topics()

    topic_data = None
    ai_gen = AIScriptGenerator()

    if force_topic:
        print(f"[Pipeline] [+] Usando tema del catálogo: '{force_topic}'", flush=True)
        topic_data = get_wildlife_topic(force_topic)
    else:
        topic_data = ai_gen.generate_wildlife_script(seen_topics=seen_topics)
        if not topic_data:
            all_topics = get_all_wildlife_topics()
            seen_normalized = {s.lower().replace("-", "_").strip() for s in seen_topics}
            
            # Filtrar temas que nunca hayan sido publicados (ni por clave, ni por slug, ni por nombre)
            available = []
            for k in all_topics:
                item = WILDLIFE_CATALOG[k]
                k_norm = k.lower().replace("-", "_")
                t_id_norm = item.get("topic_id", "").lower().replace("-", "_")
                c_name = item.get("creature_name", "").lower().replace("-", "_")
                
                already_seen = any(
                    k_norm in s or s in k_norm or
                    t_id_norm in s or s in t_id_norm or
                    (len(c_name) > 3 and c_name in s)
                    for s in seen_normalized
                )
                if not already_seen:
                    available.append(k)
                    
            chosen_key = available[0] if available else all_topics[0]
            print(f"[Pipeline] [!] Usando tema del catálogo de respaldo: '{chosen_key}' (Disponibles nuevos: {len(available)})", flush=True)
            topic_data = WILDLIFE_CATALOG[chosen_key]

    topic_id = topic_data.get("topic_id", "WILDLIFE-DOC").lower().replace(" ", "-")
    title = topic_data.get("title", "This Creature Looks Like a Monster!")
    creature_name = topic_data.get("creature_name", topic_id.replace("-", " "))
    hashtags = topic_data.get("hashtags", ["#wildlife", "#animals", "#nature", "#predators", "#shorts"])

    # 6 Actos Narrativos
    acts = [
        {"label": "Hook", "text": topic_data.get("act1_hook", ""), "is_hook": True, "is_cta": False},
        {"label": "Monster Scale", "text": topic_data.get("act2_scale", ""), "is_hook": False, "is_cta": False},
        {"label": "Stealth & Strike", "text": topic_data.get("act3_hunt", ""), "is_hook": False, "is_cta": False},
        {"label": "Death Stare / Trait", "text": topic_data.get("act4_behavior", ""), "is_hook": False, "is_cta": False},
        {"label": "Twist / Vulnerability", "text": topic_data.get("act5_twist", ""), "is_hook": False, "is_cta": False},
        {"label": "Climax & CTA", "text": topic_data.get("act6_climax_cta", ""), "is_hook": False, "is_cta": True}
    ]

    print(f"[Pipeline] [+] Criatura: '{creature_name.upper()}' (Slug: {topic_id})", flush=True)
    print(f"[Pipeline] [+] Título: {title}", flush=True)
    print(f"[Pipeline] [+] Voz: {voice_key}", flush=True)

    voice_engine = VoiceEngine(voice_key=voice_key)
    media_manager = MediaManager(temp_dir=TEMP_DIR)
    subtitle_engine = SubtitleEngine(aspect_ratio="vertical")
    composer = VideoComposer(aspect_ratio="vertical")

    scenes = []
    scene_audio_files = []
    processed_clip_files = []
    global_time = 0.0
    total_shot_counter = 0
    media_manager.reset_session()

    for idx, act in enumerate(acts):
        act_idx = idx + 1
        text = act["text"].strip()
        label = act["label"]
        print(f"\n--- [Acto {act_idx}/6: {label}] ---", flush=True)
        print(f"Narrativa: \"{text}\"", flush=True)

        synth = voice_engine.synthesize_scene(text, idx)
        audio_path = synth["audio_path"]
        word_timings = synth["word_timings"]
        act_duration = synth["duration"]
        print(f"[Voz] Duración del Acto: {act_duration:.2f}s | Palabras: {len(word_timings)}", flush=True)

        num_sub_shots = max(1, round(act_duration / PACING_SETTINGS["max_shot_duration"]))
        sub_shot_duration = act_duration / num_sub_shots
        print(f"[Multi-Clip] Dividiendo acto en {num_sub_shots} tomas dinámicas ({sub_shot_duration:.2f}s c/u)...", flush=True)

        from core.visual_director import generate_scene_search_plan
        shots_plan = generate_scene_search_plan(
            creature_name=creature_name,
            act_num=act_idx,
            act_name=label,
            act_text=text,
            num_shots=num_sub_shots
        )

        for s_idx, shot_info in enumerate(shots_plan):
            total_shot_counter += 1
            action_desc = shot_info["action_desc"]
            search_queries = shot_info["search_queries"]
            print(f"[Director Visual] Toma {total_shot_counter} -> Acción: '{action_desc}'", flush=True)

            raw_clip = media_manager.fetch_clip_for_scene(
                scene_id=total_shot_counter,
                keywords=search_queries,
                required_subject=creature_name.lower(),
                action_description=action_desc,
                target_duration=sub_shot_duration
            )

            norm_clip = TEMP_DIR / f"shot_{total_shot_counter:02d}_norm.mp4"
            composer.process_scene_clip(raw_clip, norm_clip, sub_shot_duration)
            processed_clip_files.append(norm_clip)

        scene_audio_files.append(audio_path)

        scene_dict = {
            "index": idx,
            "act_num": act_idx,
            "text": text,
            "is_hook": act["is_hook"],
            "is_cta": act["is_cta"],
            "duration": act_duration,
            "global_start": global_time,
            "word_timings": word_timings,
            "audio_path": audio_path
        }
        scenes.append(scene_dict)
        global_time += act_duration

    print(f"\n[Pipeline] [+] Total de Tomas Dinámicas Ensambladas: {len(processed_clip_files)} cortes")
    print(f"[Pipeline] [+] Duración Total del Video: {global_time:.2f}s")

    # 3. Ensamblado y Subtítulos
    video_concat_raw = TEMP_DIR / f"wildlife_{topic_id}_video_raw.mp4"
    audio_concat = TEMP_DIR / f"wildlife_{topic_id}_voice.mp3"
    subtitles_ass = TEMP_DIR / f"wildlife_{topic_id}_karaoke.ass"
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output = OUTPUT_DIR / f"wildlife_{topic_id}_{timestamp_str}.mp4"

    composer.concatenate_video_clips(processed_clip_files, video_concat_raw)
    scene_durs = [s["duration"] for s in scenes]
    whoosh_path = SFX_DIR / "cinematic_whoosh.wav"
    generate_cinematic_whoosh(whoosh_path)
    composer.concatenate_audio_tracks_with_sfx(scene_audio_files, scene_durs, whoosh_path, audio_concat)

    # Música de Fondo Cinemática
    music_path = MUSIC_DIR / "ambient_music.wav"
    generate_ambient_cinematic_music(music_path, duration=global_time + 5.0)

    print("[Subtitles] Quemando subtítulos GRANDES con sincronización acústica...", flush=True)
    subtitle_engine.create_ass_subtitles(scenes, subtitles_ass, global_time)

    composer.build_final_video(
        video_path=video_concat_raw,
        voice_audio_path=audio_concat,
        ass_subtitles_path=subtitles_ass,
        output_final_path=final_output,
        total_duration=global_time,
        bg_music_path=music_path
    )

    print(f"\n[Pipeline] [¡VIDEO GENERADO CON ÉXITO! 🎬] -> {final_output}")

    # Guardar metadatos y registrar historial
    meta_path = OUTPUT_DIR / f"metadata_{topic_id}_{timestamp_str}.txt"
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\n\nDESCRIPTION:\n{title}\n\n" + " ".join(hashtags) + "\n")
    history.record_published_topic(topic_id, title)

    # Publicación Automática en Facebook Reels (Wild Vault)
    if auto_publish:
        fb_pub = FacebookPublisher()
        if fb_pub.is_configured():
            auto_comment = (
                f"🔥 WILD VAULT QUESTION: Have you ever seen a {creature_name} up close in real life? "
                f"Rate its power from 1 to 10 below! 👇🐾\n\n"
                f"💡 Notice: This educational video was created with AI assistance. Follow @WildVault for daily 4K wildlife shorts!"
            )
            fb_pub.publish_reel(
                video_path=final_output,
                title=title,
                description=f"Discover the untamed secrets of the {creature_name}! 🦅🌿 Which fact surprised you the most?",
                hashtags=" ".join(hashtags),
                comment_text=auto_comment
            )

    print(f"\n=================================================================")
    print(f"  🎉 MICRO-DOC COMPLETADO CON ÉXITO")
    print(f"  Criatura: {creature_name} | Cortes: {len(processed_clip_files)} tomas | Archivo: {final_output.name}")
    print(f"=================================================================\n", flush=True)

    return final_output

# =====================================================================
#  MODO 2: TOPS / CUENTA REGRESIVA (#3, #2, #1) ESTILO YOUTUBE SHORTS
# =====================================================================
def run_top_countdown_pipeline(force_topic: str = "", voice_key: str = DEFAULT_VOICE, auto_publish: bool = True) -> Path:
    print("\n" + "=" * 65)
    print("  🏆 MODO 2: TOPS / CUENTA REGRESIVA (#3, #2, #1) SHORTS 📹")
    print("=" * 65 + "\n", flush=True)

    history = HistoryManager(Path("history.json"))
    seen_topics = history.get_seen_topics()

    topic_data = None
    ai_top_gen = AITopGenerator()

    if force_topic:
        print(f"[Pipeline] [+] Usando Top del catálogo: '{force_topic}'", flush=True)
        topic_data = get_top_topic(force_topic)
    else:
        topic_data = ai_top_gen.generate_top_script(seen_topics=seen_topics)
        if not topic_data:
            all_tops = get_all_top_topics()
            available = [t for t in all_tops if t not in seen_topics]
            chosen_key = available[0] if available else all_tops[0]
            print(f"[Pipeline] [!] Usando Top del catálogo de respaldo: '{chosen_key}'", flush=True)
            topic_data = TOP_CATALOG[chosen_key]

    topic_id = topic_data.get("topic_id", "TOP-ANIMALS").lower().replace(" ", "-")
    title = topic_data.get("title", "Top 3 Shocking Animal Encounters Caught on Camera!")
    hook_text = topic_data.get("hook", "Here are the top three most terrifying animal encounters!")
    items = topic_data.get("items", [])
    climax_cta = topic_data.get("climax_cta", "Which one shocked you the most? Drop your vote in the comments!")
    hashtags = topic_data.get("hashtags", ["#wildlife", "#animals", "#top3", "#caughtoncamera", "#shorts"])

    print(f"[Pipeline] [+] Top: '{title}' (Slug: {topic_id})", flush=True)
    print(f"[Pipeline] [+] Puestos: {len(items)} items (#3 a #1)", flush=True)
    print(f"[Pipeline] [+] Voz: {voice_key}", flush=True)

    voice_engine = VoiceEngine(voice_key=voice_key)
    media_manager = MediaManager(temp_dir=TEMP_DIR)
    subtitle_engine = SubtitleEngine(aspect_ratio="vertical")
    composer = VideoComposer(aspect_ratio="vertical")

    scenes = []
    scene_audio_files = []
    processed_clip_files = []
    global_time = 0.0
    total_shot_counter = 0
    media_manager.reset_session()

    # 1. Gancho Inicial del Top (0-4s)
    print(f"\n--- [Sección: Gancho del Top] ---", flush=True)
    print(f"Narrativa: \"{hook_text}\"", flush=True)
    hook_synth = voice_engine.synthesize_scene(hook_text, 0)
    hook_audio = hook_synth["audio_path"]
    hook_timings = hook_synth["word_timings"]
    hook_dur = hook_synth["duration"]
    print(f"[Voz] Duración del Gancho: {hook_dur:.2f}s", flush=True)

    # Clip inicial de alta tensión dinámico para el Top
    first_creature = items[-1].get("creature_name", "predator") if items else "predator"
    total_shot_counter += 1
    raw_hook_clip = media_manager.fetch_clip_for_scene(
        scene_id=total_shot_counter,
        keywords=[f"{first_creature} predator attack strike 4k", f"{first_creature} extreme close up eyes 4k", f"{first_creature} wild hunting"],
        required_subject=first_creature,
        action_description="predator_reveal",
        target_duration=hook_dur
    )
    norm_hook = TEMP_DIR / f"shot_{total_shot_counter:02d}_norm.mp4"
    composer.process_scene_clip(raw_hook_clip, norm_hook, hook_dur)
    processed_clip_files.append(norm_hook)
    scene_audio_files.append(hook_audio)

    scenes.append({
        "index": 0,
        "act_num": 1,
        "text": hook_text,
        "is_hook": True,
        "is_cta": False,
        "duration": hook_dur,
        "global_start": global_time,
        "word_timings": hook_timings,
        "audio_path": hook_audio
    })
    global_time += hook_dur

    # 2. Puestos del Top (#3, #2, #1)
    for idx, item in enumerate(items, 1):
        rank = item.get("rank", 4 - idx)
        badge = item.get("badge", f"#{rank}")
        creature = item.get("creature_name", "predator")
        item_text = item.get("text", "")
        action = item.get("action_type", "explosive_strike")

        print(f"\n--- [PUESTO #{rank}: {badge} - {creature.upper()}] ---", flush=True)
        print(f"Narrativa: \"{item_text}\"", flush=True)

        item_synth = voice_engine.synthesize_scene(item_text, idx)
        item_audio = item_synth["audio_path"]
        item_timings = item_synth["word_timings"]
        item_dur = item_synth["duration"]
        print(f"[Voz] Duración Puesto #{rank}: {item_dur:.2f}s | Palabras: {len(item_timings)}", flush=True)

        num_sub_shots = max(2, round(item_dur / PACING_SETTINGS["max_shot_duration"]))
        sub_dur = item_dur / num_sub_shots
        print(f"[Multi-Clip] Dividiendo Puesto #{rank} en {num_sub_shots} tomas dinámicas de '{creature}' ({sub_dur:.2f}s c/u)...", flush=True)

        for s_idx in range(num_sub_shots):
            total_shot_counter += 1
            cur_action = action if s_idx > 0 else "predator_reveal"
            print(f"[Director Top] Puesto #{rank} -> Toma {total_shot_counter} ({creature} - {cur_action})", flush=True)

            raw_clip = media_manager.fetch_clip_for_scene(
                scene_id=total_shot_counter,
                keywords=[f"{creature} {cur_action} 4k", f"{creature} close up 4k", f"{creature} wildlife"],
                required_subject=creature.lower(),
                action_description=cur_action,
                target_duration=sub_dur
            )

            norm_clip = TEMP_DIR / f"shot_{total_shot_counter:02d}_norm.mp4"
            composer.process_scene_clip(raw_clip, norm_clip, sub_dur)
            processed_clip_files.append(norm_clip)

        scene_audio_files.append(item_audio)
        scenes.append({
            "index": idx,
            "act_num": idx + 1,
            "text": item_text,
            "is_hook": False,
            "is_cta": False,
            "duration": item_dur,
            "global_start": global_time,
            "word_timings": item_timings,
            "audio_path": item_audio
        })
        global_time += item_dur

    # 3. Cierre y Llamado a la Acción (CTA)
    print(f"\n--- [Sección: Cierre del Top] ---", flush=True)
    print(f"Narrativa: \"{climax_cta}\"", flush=True)
    cta_synth = voice_engine.synthesize_scene(climax_cta, len(items) + 1)
    cta_audio = cta_synth["audio_path"]
    cta_timings = cta_synth["word_timings"]
    cta_dur = cta_synth["duration"]
    print(f"[Voz] Duración Cierre: {cta_dur:.2f}s", flush=True)

    total_shot_counter += 1
    last_creature = items[-1].get("creature_name", "jaguar")
    raw_cta_clip = media_manager.fetch_clip_for_scene(
        scene_id=total_shot_counter,
        keywords=[f"{last_creature} roar open mouth 4k", f"{last_creature} dramatic close up 4k"],
        required_subject=last_creature.lower(),
        action_description="climax_dramatic",
        target_duration=cta_dur
    )
    norm_cta = TEMP_DIR / f"shot_{total_shot_counter:02d}_norm.mp4"
    composer.process_scene_clip(raw_cta_clip, norm_cta, cta_dur)
    processed_clip_files.append(norm_cta)
    scene_audio_files.append(cta_audio)

    scenes.append({
        "index": len(items) + 1,
        "act_num": len(items) + 2,
        "text": climax_cta,
        "is_hook": False,
        "is_cta": True,
        "duration": cta_dur,
        "global_start": global_time,
        "word_timings": cta_timings,
        "audio_path": cta_audio
    })
    global_time += cta_dur

    print(f"\n[Pipeline] [+] Total de Tomas Dinámicas Ensambladas: {len(processed_clip_files)} cortes")
    print(f"[Pipeline] [+] Duración Total del Top: {global_time:.2f}s")

    # 4. Ensamblado y Subtítulos
    video_concat_raw = TEMP_DIR / f"top_{topic_id}_video_raw.mp4"
    audio_concat = TEMP_DIR / f"top_{topic_id}_voice.mp3"
    subtitles_ass = TEMP_DIR / f"top_{topic_id}_karaoke.ass"
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output = OUTPUT_DIR / f"top_{topic_id}_{timestamp_str}.mp4"

    composer.concatenate_video_clips(processed_clip_files, video_concat_raw)
    scene_durs = [s["duration"] for s in scenes]
    whoosh_path = SFX_DIR / "cinematic_whoosh.wav"
    generate_cinematic_whoosh(whoosh_path)
    composer.concatenate_audio_tracks_with_sfx(scene_audio_files, scene_durs, whoosh_path, audio_concat)

    # Música de Fondo Cinemática
    music_path = MUSIC_DIR / "ambient_music.wav"
    generate_ambient_cinematic_music(music_path, duration=global_time + 5.0)

    print("[Subtitles] Quemando subtítulos Karaoke y badges de cuenta regresiva...", flush=True)
    subtitle_engine.create_ass_subtitles(scenes, subtitles_ass, global_time)

    composer.build_final_video(
        video_path=video_concat_raw,
        voice_audio_path=audio_concat,
        ass_subtitles_path=subtitles_ass,
        output_final_path=final_output,
        total_duration=global_time,
        bg_music_path=music_path
    )

    print(f"\n[Pipeline] [¡VIDEO TOP GENERADO CON ÉXITO! 🎬] -> {final_output}")

    meta_path = OUTPUT_DIR / f"metadata_{topic_id}_{timestamp_str}.txt"
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\n\nDESCRIPTION:\n{title}\n\n" + " ".join(hashtags) + "\n")
    history.record_published_topic(topic_id, title)

    # Publicación Automática en Facebook Reels (Wild Vault)
    if auto_publish:
        fb_pub = FacebookPublisher()
        if fb_pub.is_configured():
            auto_comment = (
                f"🔥 WILD VAULT POLL: Which of these 3 creatures would win in an ultimate survival showdown? "
                f"Drop your vote below! 💬👇\n\n"
                f"💡 Notice: This educational countdown was created with AI assistance. Follow @WildVault for daily wildlife battles!"
            )
            fb_pub.publish_reel(
                video_path=final_output,
                title=title,
                description=f"{title}\n\nWhich moment shocked you the most? Drop your vote in the comments and follow Wild Vault!",
                hashtags=" ".join(hashtags),
                comment_text=auto_comment
            )

    print(f"\n=================================================================")
    print(f"  🎉 TOP 3 CUENTA REGRESIVA COMPLETADO CON ÉXITO")
    print(f"  Título: {title} | Cortes: {len(processed_clip_files)} tomas | Archivo: {final_output.name}")
    print(f"=================================================================\n", flush=True)

    return final_output

# =====================================================================
#  PUNTO DE ENTRADA PRINCIPAL (CLI)
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="Wildlife Video Engine - Micro-Docs & Top Countdowns")
    parser.add_argument("--mode", type=str, choices=["single", "top", "auto"], default="single",
                        help="Modo de generación: 'single' (Micro-Doc 1 animal), 'top' (Cuenta regresiva #3-#1), 'auto' (alterna)")
    parser.add_argument("--topic", type=str, default="", help="ID o nombre del tema a forzar")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Voz TTS a utilizar")
    parser.add_argument("--no-publish", action="store_true", help="No publicar automáticamente")

    args = parser.parse_args()

    mode = args.mode
    if mode == "auto":
        mode = random.choice(["single", "top"])

    if mode == "top":
        run_top_countdown_pipeline(force_topic=args.topic, voice_key=args.voice, auto_publish=not args.no_publish)
    else:
        run_single_creature_pipeline(force_topic=args.topic, voice_key=args.voice, auto_publish=not args.no_publish)

if __name__ == "__main__":
    main()
