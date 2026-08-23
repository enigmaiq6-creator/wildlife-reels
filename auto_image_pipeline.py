import os
import sys
import time
import argparse
import random
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

from config import OUTPUT_DIR, TEMP_DIR
from graphics.font_manager import FontManager
from graphics.image_engine import ImageEngine
from graphics.content_generator import ContentGenerator
from fetchers.gcp_vertex_image_generator import GCPVertexImageGenerator
from publisher.facebook_publisher import FacebookPublisher
from core.history_manager import HistoryManager

def ensure_image_generated(prompt: str, target_path: Path, max_retries: int = 3) -> bool:
    """
    Garantiza que la imagen del animal se genere con éxito (Vertex AI o Respaldo IA)
    y tenga un tamaño válido (> 5KB) antes de proceder con el ensamble gráfico.
    """
    target_path.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(max_retries):
        if target_path.exists() and target_path.stat().st_size > 5000:
            return True
        success = GCPVertexImageGenerator.generate_image(prompt, target_path)
        if success and target_path.exists() and target_path.stat().st_size > 5000:
            return True
        print(f"[ImagePipeline] [!] Reintentando generación de imagen ({attempt + 1}/{max_retries}) para '{prompt[:35]}...'")
        time.sleep(2)
    return target_path.exists() and target_path.stat().st_size > 5000

def run_image_pipeline(forced_format: str = "", auto_publish: bool = True) -> Optional[Path]:
    """
    Ejecuta el pipeline autónomo de generación y publicación de imágenes para Wild Vault.
    1. Selecciona un formato aleatorio entre los 8 disponibles.
    2. Genera los activos visuales con Google Cloud Vertex AI / Respaldo IA garantizado.
    3. Valida que NINGUNA imagen quede negra o vacía.
    4. Ensambla la composición gráfica en 1080x1350 con ImageEngine.
    5. Genera la descripción contextual en inglés y publica automáticamente en Facebook.
    """
    print("\n" + "=" * 65)
    print("  🎨 MOTOR AUTÓNOMO DE IMÁGENES MULTI-FORMATO (WILD VAULT) 🌿")
    print("=" * 65 + "\n", flush=True)

    img_output_dir = OUTPUT_DIR / "images"
    img_output_dir.mkdir(parents=True, exist_ok=True)
    temp_dir = TEMP_DIR / "image_gen"
    temp_dir.mkdir(parents=True, exist_ok=True)

    history = HistoryManager()
    seen_topics = history.get_seen_topics()

    # 1. Seleccionar formato y tema
    format_type, topic_data = ContentGenerator.get_random_topic(
        format_type=forced_format if forced_format else None,
        seen_topic_ids=seen_topics
    )
    topic_id = topic_data.get("topic_id", f"IMG-{int(time.time())}")
    caption = topic_data.get("caption", "🌿 Discover the most breathtaking secrets of wildlife on planet Earth with Wild Vault.")

    # Añadir hashtags de marca en inglés
    full_caption = caption + "\n\n#WildVault #Wildlife #Nature #Animals #NatureLovers #WildFacts #Science"

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_output_path = img_output_dir / f"wildvault_{format_type}_{topic_id.lower()}_{timestamp_str}.jpg"

    print(f"[ImagePipeline] [+] Formato Seleccionado: '{format_type}'")
    print(f"[ImagePipeline] [+] Tema ID: '{topic_id}'")

    # 2. Generar imágenes y renderizar según el formato elegido
    if format_type == "format_1_taxonomic_catalog":
        title = topic_data.get("title", "8 Types of Species")
        species_raw = topic_data.get("species", [])
        rendered_species = []
        for s_idx, sp in enumerate(species_raw):
            sp_img_p = temp_dir / f"sp_{s_idx}.jpg"
            ensure_image_generated(sp.get("prompt", ""), sp_img_p)
            rendered_species.append({
                "name": sp.get("name", ""),
                "scientific": sp.get("scientific", ""),
                "image_path": sp_img_p
            })
            time.sleep(1) # Espaciado para evitar 429
        ImageEngine.render_format_1_taxonomic_catalog(title, rendered_species, final_output_path)

    elif format_type == "format_2_real_vs_illustrated":
        top_p = temp_dir / "real.jpg"
        bot_p = temp_dir / "illustrated.jpg"
        ensure_image_generated(topic_data.get("prompt_real", ""), top_p)
        time.sleep(1)
        ensure_image_generated(topic_data.get("prompt_illustrated", ""), bot_p)
        dialogue = topic_data.get("dialogue", "Can we be friends?")
        ImageEngine.render_format_2_real_vs_illustrated(top_p, bot_p, dialogue, final_output_path)

    elif format_type == "format_3_curiosity_pip":
        main_p = temp_dir / "main.jpg"
        pip_p = temp_dir / "pip.jpg"
        ensure_image_generated(topic_data.get("prompt_main", ""), main_p)
        time.sleep(1)
        ensure_image_generated(topic_data.get("prompt_pip", ""), pip_p)
        badge = topic_data.get("badge", "RARE DISCOVERY")
        headline = topic_data.get("headline", ["AMAZING CREATURE", "DISCOVERY"])
        ImageEngine.render_format_3_curiosity_pip(main_p, pip_p, headline, final_output_path, badge_text=badge)

    elif format_type == "format_5_creature_profile":
        profile_p = temp_dir / "profile.jpg"
        ensure_image_generated(topic_data.get("prompt", ""), profile_p)
        title = topic_data.get("title", "The Nautilus")
        paragraphs = topic_data.get("paragraphs", [])
        ImageEngine.render_format_5_creature_profile(profile_p, title, paragraphs, final_output_path)

    elif format_type == "format_6_vintage_guide":
        title = topic_data.get("title", "The 9 Most Dangerous Species")
        species_raw = topic_data.get("species", [])
        rendered_species = []
        for s_idx, sp in enumerate(species_raw):
            sp_img_p = temp_dir / f"vintage_{s_idx}.jpg"
            ensure_image_generated(sp.get("prompt", ""), sp_img_p)
            rendered_species.append({
                "name": sp.get("name", ""),
                "sci": sp.get("sci", ""),
                "desc": sp.get("desc", ""),
                "image_path": sp_img_p
            })
            time.sleep(1) # Espaciado para evitar 429
        ImageEngine.render_format_6_vintage_guide(title, rendered_species, final_output_path)

    elif format_type == "format_7_breaking_news":
        news_p = temp_dir / "news.jpg"
        ensure_image_generated(topic_data.get("prompt", ""), news_p)
        headline = topic_data.get("headline", "Breaking Prehistoric Discovery")
        ImageEngine.render_format_7_breaking_news(news_p, headline, final_output_path)

    elif format_type == "format_8_quad_collage":
        prompts = topic_data.get("prompts", [])
        quad_paths = []
        for q_idx, pr in enumerate(prompts[:4]):
            qp = temp_dir / f"quad_{q_idx}.jpg"
            ensure_image_generated(pr, qp)
            quad_paths.append(qp)
            time.sleep(1)
        title = topic_data.get("title", "4 TITANS OF NATURE")
        ImageEngine.render_format_8_quad_collage(quad_paths, final_output_path, overlay_title=title)

    # Validar que la imagen final compilada exista y no esté vacía
    if not final_output_path.exists() or final_output_path.stat().st_size < 10000:
        print(f"[ImagePipeline] [!] Error crítico: La imagen compilada en {final_output_path} es inválida. Abortando subida.")
        return None

    print(f"\n[ImagePipeline] [¡IMAGEN COMPILADA CON ÉXITO! 🎨] ({final_output_path.stat().st_size / 1024:.1f} KB) -> {final_output_path}")

    # 3. Guardar registro en el historial
    history.record_published_topic(topic_id, f"IMAGE_{format_type}")

    # 4. Publicar automáticamente en Facebook Page (Wild Vault)
    if auto_publish:
        fb_pub = FacebookPublisher()
        if fb_pub.is_configured():
            fb_pub.publish_photo(
                image_path=final_output_path,
                caption=full_caption
            )

    print(f"\n=================================================================")
    print(f"  🎉 PUBLICACIÓN DE IMAGEN COMPLETADA CON ÉXITO")
    print(f"  Formato: {format_type} | Archivo: {final_output_path.name}")
    print(f"=================================================================\n", flush=True)

    return final_output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wild Vault Image Engine Pipeline")
    parser.add_argument("--format", type=str, default="", help="Forzar formato específico (ej. format_3_curiosity_pip)")
    parser.add_argument("--no-publish", action="store_true", help="Generar solo localmente sin publicar a Facebook")
    args = parser.parse_args()

    run_image_pipeline(forced_format=args.format, auto_publish=not args.no_publish)
