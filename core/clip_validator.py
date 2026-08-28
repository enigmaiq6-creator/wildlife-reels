import re
from typing import List, Dict, Any, Tuple, Optional
from core.wildlife_taxonomy import get_taxonomy_for_creature

# Palabras prohibidas globales que arruinan un documental de vida salvaje
GLOBAL_BANNED_WORDS = {
    # 1. Humanos, personas, caras y presentadores hablando (CERO PERSONAS HABLANDO)
    "person", "people", "man", "woman", "guy", "girl", "boy", "human", "humans",
    "tourist", "tourists", "diver", "divers", "scuba", "swimmer", "face", "faces",
    "talking", "selfie", "hands", "speaker", "presenter", "host", "narrator", 
    "influencer", "streamer", "youtuber", "vlogger", "anchor", "reacting",
    
    # 2. Formatos con subtítulos quemados, podcasts, reacciones y vlogs (CERO DOBLE SUBTÍTULO)
    "podcast", "interview", "vlog", "vlogs", "reaction", "reactions", "review", 
    "commentary", "storytime", "explaining", "explained", "subtitles", "captions", 
    "tiktok", "shorts", "reels", "challenge", "prank", "news", "studio", 
    "microphone", "mic", "podcast clip",
    
    # 3. Entornos artificiales o cautiverio
    "aquarium", "tank", "zoo", "cage", "enclosure", "pool", "swimming pool", 
    "pet", "domestic", "farm", "city", "street", "car", "traffic", "house", 
    "room", "indoor", "boat", "ship",
    
    # 4. Artefactos no reales o animaciones
    "cartoon", "animation", "3d", "3d illustration", "toy", "statue", 
    "museum", "drawing", "illustration", "puppet", "cgi", "render", "costume", "halloween",
    
    # 5. Falsos positivos
    "woodpecker", "egret", "heron", "pigeon", "beaver", "basket", "wall", "china", "beijing"
}

def validate_clip_metadata(
    video_title: str,
    video_tags: str,
    target_creature: str,
    target_action: str = ""
) -> Tuple[bool, int, str]:
    """
    Valida y puntúa estrictamente si un video corresponde al animal y acción del guion
    utilizando el mapa taxonómico y familiar de vida salvaje.
    """
    text_to_check = f"{video_title} {video_tags}".lower().replace("-", " ").replace("_", " ")
    
    # 1. Comprobar lista negra global (Cero humanos, cero podcasts, cero animaciones)
    for banned in GLOBAL_BANNED_WORDS:
        if re.search(r'\b' + re.escape(banned) + r'\b', text_to_check):
            return False, -100, f"Contiene palabra prohibida global: '{banned}'"

    # 2. Obtener reglas taxonómicas de la criatura
    tax = get_taxonomy_for_creature(target_creature)

    # Comprobar palabras prohibidas específicas de la criatura/familia
    for spec_banned in tax.get("banned", []):
        if re.search(r'\b' + re.escape(spec_banned) + r'\b', text_to_check):
            return False, -100, f"Contiene contexto prohibido: '{spec_banned}'"

    # Comprobar que contenga al menos uno de los términos requeridos de la especie o su familia
    has_required = False
    matched_term = ""
    terms_to_check = tax.get("required_any", [])
    for req in terms_to_check:
        if req and re.search(r'\b' + re.escape(req.lower()) + r'\b', text_to_check):
            has_required = True
            matched_term = req
            break

    if not has_required:
        return False, 0, f"No contiene términos taxonómicos de '{target_creature}' ({terms_to_check})"

    # 3. Calcular puntuación de relevancia
    score = 50  # Puntuación base por coincidencia familiar/especie
    
    creature_clean = target_creature.lower().replace("-", " ").replace("_", " ").strip()
    if creature_clean in text_to_check:
        score += 35

    # Bonificación por coincidencia con la acción del guion (ej. "teeth", "hunting", "breach", "eyes")
    if target_action:
        action_words = [w for w in re.findall(r'\b[a-z]{3,}\b', target_action.lower()) if w not in GLOBAL_BANNED_WORDS]
        for act_w in action_words:
            if act_w in text_to_check:
                score += 15

    return True, score, f"Aprobado (Match: '{matched_term}', Score: {score})"

