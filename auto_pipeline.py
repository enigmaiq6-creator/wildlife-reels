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
    SUBTITLE_CONFIG,
    PACING_SETTINGS
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
    print("  🦅 WILDLIFE ENGINE: MULTI-CLIP & BIG SUBTITLES (ARES G STYLE) 🌿")
    print("=" * 65 + "\n", flush=True)

    history = HistoryManager(Path("history.json"))
    seen_topics = history.get_seen_topics()

    topic_data = None
    ai_gen = AIScriptGenerator()

    # 1. Generación / Selección del Micro-Documental
    if force_topic:
        print(f"[Pipeline] [+] Usando tema del catálogo: '{force_topic}'", flush=True)
        topic_data = get_wildlife_topic(force_topic)
    else:
        topic_data = ai_gen.generate_wildlife_script(seen_topics=seen_topics)
        if not topic_data:
            all_topics = get_all_wildlife_topics()
            available = [t for t in all_topics if t not in seen_topics]
            chosen_key = available[0] if available else all_topics[0]
            print(f"[Pipeline] [!] Usando tema del catálogo de respaldo: '{chosen_key}'", flush=True)
            topic_data = WILDLIFE_CATALOG[chosen_key]

    topic_id = topic_data.get("topic_id", "WILDLIFE-DOC").lower().replace(" ", "-")
    title = topic_data.get("title", "This Creature Looks Like a Monster!")
    creature_name = topic_data.get("creature_name", topic_id.replace("-", " "))
    keywords = topic_data.get("pexels_keywords", [])
    hashtags = topic_data.get("hashtags", ["#wildlife", "#animals", "#nature", "#predators", "#shorts"])

    # 6 Actos Narrativos
    act1 = topic_data.get("act1_hook", "")
    act2 = topic_data.get("act2_scale", "")
    act3 = topic_data.get("act3_hunt", "")
    act4 = topic_data.get("act4_behavior", "")
    act5 = topic_data.get("act5_twist", "")
    act6 = topic_data.get("act6_climax_cta", "")

    print(f"[Pipeline] [+] Criatura: '{creature_name.upper()}' (Slug: {topic_id})", flush=True)
    print(f"[Pipeline] [+] Título: {title}", flush=True)
    print(f"[Pipeline] [+] Voz: {voice_key}", flush=True)

    # 2. Inicializar Motores
    voice_engine = VoiceEngine(voice_key=voice_key)
    media_manager = MediaManager(temp_dir=TEMP_DIR)
    subtitle_engine = SubtitleEngine(aspect_ratio="vertical")
    composer = VideoComposer(aspect_ratio="vertical")

    scenes = []
    scene_audio_files = []
    processed_clip_files = []
    global_time = 0.0

    raw_acts = [
        {"act_num": 1, "name": "Hook", "text": act1, "is_hook": True, "is_cta": False, "kw": keywords[0] if len(keywords) > 0 else f"{creature_name} close up 4k"},
        {"act_num": 2, "name": "Monster Scale", "text": act2, "is_hook": False, "is_cta": False, "kw": keywords[1] if len(keywords) > 1 else f"{creature_name} head dinosaur 4k"},
        {"act_num": 3, "name": "Stealth & Strike", "text": act3, "is_hook": False, "is_cta": False, "kw": keywords[2] if len(keywords) > 2 else f"{creature_name} hunting attack 4k"},
        {"act_num": 4, "name": "Death Stare / Trait", "text": act4, "is_hook": False, "is_cta": False, "kw": keywords[3] if len(keywords) > 3 else f"{creature_name} stare eyes camera 4k"},
        {"act_num": 5, "name": "Twist / Vulnerability", "text": act5, "is_hook": False, "is_cta": False, "kw": keywords[4] if len(keywords) > 4 else f"{creature_name} walking nature 4k"},
        {"act_num": 6, "name": "Climax & CTA", "text": act6, "is_hook": False, "is_cta": True, "kw": keywords[5] if len(keywords) > 5 else f"{creature_name} sound mouth 4k"}
    ]

    total_shot_counter = 0

    # Procesar cada acto dividiéndolo en múltiples tomas dinámicas (cortes cada 2.5 - 3.5s)
    for idx, act in enumerate(raw_acts):
        act_idx = act["act_num"]
        label = act["name"]
        text = act["text"]
        base_kw = act["kw"]

        print(f"\n--- [Acto {act_idx}/6: {label}] ---", flush=True)
        print(f"Narrativa: \"{text}\"", flush=True)

        # Sintetizar audio del acto completo
        audio_data = voice_engine.synthesize_scene(text, idx)
        act_duration = audio_data["duration"]
        word_timings = audio_data["word_timings"]
        audio_path = audio_data["audio_path"]
        print(f"[Voz] Duración del Acto: {act_duration:.2f}s | Palabras: {len(word_timings)}", flush=True)

        # Calcular número de tomas requeridas para este acto (máx 3.5 segundos por toma)
        num_sub_shots = max(1, round(act_duration / PACING_SETTINGS["max_shot_duration"]))
        sub_shot_duration = act_duration / num_sub_shots
        print(f"[Multi-Clip] Dividiendo acto en {num_sub_shots} tomas dinámicas ({sub_shot_duration:.2f}s c/u)...", flush=True)

        # Descargar y procesar clips variados para cada sub-toma
        for s_idx in range(num_sub_shots):
            total_shot_counter += 1
            # Variaciones de búsqueda para cada ángulo de cámara
            angle_variations = [
                base_kw,
                f"{creature_name} close up 4k vertical",
                f"{creature_name} eyes looking camera 4k",
                f"{creature_name} hunting slow motion 4k",
                f"{creature_name} walking wild 4k",
                f"{creature_name} wildlife 4k vertical"
            ]
            chosen_kw = angle_variations[(s_idx + act_idx) % len(angle_variations)]
            
            # Descargar clip verificado
            raw_clip = media_manager.fetch_clip_for_scene(
                scene_id=total_shot_counter,
                keywords=[chosen_kw, f"{creature_name} 4k", f"{creature_name} wildlife"],
                required_subject=creature_name.split()[0].lower(),
                target_duration=sub_shot_duration
            )

            # Normalizar clip a 1080x1920 con micro-zoom Ken Burns
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

    total_duration = global_time
    print(f"\n[Pipeline] [+] Total de Tomas Dinámicas Ensambladas: {len(processed_clip_files)} cortes", flush=True)
    print(f"[Pipeline] [+] Duración Total del Video: {total_duration:.2f}s", flush=True)

    # 3. Concatenar clips de video y pistas de audio
    video_base_path = TEMP_DIR / f"wildlife_{topic_id}_base.mp4"
    audio_base_path = TEMP_DIR / f"wildlife_{topic_id}_audio.mp3"

    print(f"[Composer] Concatenando {len(processed_clip_files)} clips a 30 FPS constantes...", flush=True)
    composer.concatenate_video_clips(processed_clip_files, video_base_path)

    # Efectos de sonido Whoosh
    whoosh_path = SFX_DIR / "whoosh.wav"
    if not whoosh_path.exists():
        generate_cinematic_whoosh(whoosh_path)

    scene_durations = [s["duration"] for s in scenes]
    print("[Composer] Concatenando audio con transiciones de suspenso...", flush=True)
    composer.concatenate_audio_tracks_with_sfx(
        scene_audio_files,
        scene_durations,
        whoosh_path,
        audio_base_path
    )

    # 4. Generar Subtítulos Grandes ASS
    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    ass_path = TEMP_DIR / f"subtitles_{topic_id}_{timestamp_str}.ass"
    print("[Subtitles] Quemando subtítulos GRANDES (Tamaño 60-76) con sincronización acústica...", flush=True)
    subtitle_engine.create_ass_subtitles(scenes, ass_path, total_duration)

    # 5. Render Final 1080x1920 con Subtítulos Grandes y Música
    output_filename = f"wildlife_{topic_id}_{timestamp_str}.mp4"
    final_output_path = OUTPUT_DIR / output_filename

    # Música ambiental
    bg_music_path = MUSIC_DIR / "ambient_nature.wav"
    if not bg_music_path.exists():
        generate_ambient_cinematic_music(bg_music_path, duration=total_duration + 5.0)

    print(f"[Composer] Renderizando video final -> {output_filename}...", flush=True)
    composer.build_final_video(
        video_path=video_base_path,
        voice_audio_path=audio_base_path,
        ass_subtitles_path=ass_path,
        output_final_path=final_output_path,
        total_duration=total_duration,
        bg_music_path=bg_music_path
    )
    print(f"\n[Pipeline] [¡VIDEO GENERADO CON ÉXITO! 🎬] -> {final_output_path}", flush=True)

    # 6. Guardar Metadatos
    description = f"{title}\n\n{act1}\n\n" + "\n".join(hashtags)
    metadata_path = OUTPUT_DIR / f"metadata_{topic_id}_{timestamp_str}.txt"
    with open(metadata_path, "w", encoding="utf-8") as f:
        f.write(f"TITLE:\n{title}\n\nDESCRIPTION:\n{description}\n\nTOPIC_ID:\n{topic_id}\n")
    print(f"[Pipeline] [+] Metadatos guardados en: {metadata_path.name}", flush=True)

    # 7. Publicación en Meta (si está activa)
    fb_post_id = ""
    if auto_publish:
        fb_uploader = FacebookUploader()
        fb_res = fb_uploader.upload_reel(final_output_path, description)
        if fb_res.get("success"):
            fb_post_id = str(fb_res.get("data", {}).get("post_id", ""))

        ig_uploader = InstagramUploader()
        ig_uploader.upload_reel_resumable(final_output_path, description)

    # Registrar en historial
    history.record_published_topic(topic_id, title, fb_post_id)

    print("\n" + "=" * 65)
    print(f"  🎉 PIPELINE MULTI-CLIP COMPLETADO CON ÉXITO")
    print(f"  Criatura: {creature_name} | Cortes: {len(processed_clip_files)} tomas | Archivo: {output_filename}")
    print("=" * 65 + "\n", flush=True)
    return final_output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wildlife Multi-Clip Micro-Documentary Engine")
    parser.add_argument("--topic", type=str, default="", help="Tema específico del catálogo (ej: jaguar_hunter)")
    parser.add_argument("--voice", type=str, default=DEFAULT_VOICE, help="Clave de voz neuronal")
    parser.add_argument("--no-publish", action="store_true", help="Desactivar subida automática a Meta")
    args = parser.parse_args()

    run_wildlife_pipeline(force_topic=args.topic, voice_key=args.voice, auto_publish=not args.no_publish)
