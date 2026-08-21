import re
from typing import List, Dict, Any, Tuple, Optional

# Palabras prohibidas globales que arruinan un documental de vida salvaje
GLOBAL_BANNED_WORDS = {
    "aquarium", "tank", "zoo", "cage", "diver", "divers", "scuba", "swimmer", 
    "swimming pool", "pool", "person", "human", "people", "man", "woman", 
    "tourist", "tourists", "boat", "ship", "cartoon", "animation", "3d", 
    "3d illustration", "toy", "statue", "museum", "drawing", "illustration", 
    "wall", "china", "beijing", "woodpecker", "egret", "heron", "pigeon", 
    "monkey", "beaver", "basket", "farm", "domestic", "pet", "dog", "cat", 
    "kitten", "puppy", "city", "street", "car", "traffic"
}

# Filtros negativos y positivos específicos por especie
SPECIES_RULES: Dict[str, Dict[str, Any]] = {
    "shark": {
        "required_any": ["shark", "carcharodon", "great white", "predator fish"],
        "banned": [
            "whale shark", "nurse shark", "leopard shark", "hammerhead", "basking shark",
            "sea lion", "jellyfish", "stingray", "coral only", "woodpecker", "egret", "wall"
        ],
        "primary_name": "great white shark"
    },
    "great_white_shark": {
        "required_any": ["great white", "shark", "carcharodon"],
        "banned": [
            "whale shark", "nurse shark", "leopard shark", "basking shark",
            "sea lion", "jellyfish", "stingray", "woodpecker", "egret", "wall"
        ],
        "primary_name": "great white shark"
    },
    "jaguar": {
        "required_any": ["jaguar", "panthera onca", "black panther", "wild jaguar"],
        "banned": [
            "leopard", "cheetah", "tiger", "lion", "snow leopard", "amur leopard", 
            "house cat", "kitten", "zoo", "monkey", "beaver", "basket", "man"
        ],
        "primary_name": "jaguar"
    },
    "shoebill": {
        "required_any": ["shoebill", "balaeniceps", "whalehead", "picozapato"],
        "banned": [
            "white stork", "marabou", "heron", "crane", "pelican", "flamingo", "chimney"
        ],
        "primary_name": "shoebill stork"
    },
    "shoebill_stork": {
        "required_any": ["shoebill", "balaeniceps", "whalehead", "picozapato"],
        "banned": [
            "white stork", "marabou", "heron", "crane", "pelican", "flamingo", "chimney"
        ],
        "primary_name": "shoebill stork"
    },
    "harpy_eagle": {
        "required_any": ["harpy", "harpy eagle", "harpia harpyja", "giant eagle"],
        "banned": [
            "bald eagle", "golden eagle", "pigeon", "parrot", "seagull", "owl", "hawk", "falcon"
        ],
        "primary_name": "harpy eagle"
    },
    "orca": {
        "required_any": ["orca", "killer whale", "orcinus orca"],
        "banned": [
            "humpback", "blue whale", "beluga", "dolphin", "seaworld", "aquarium"
        ],
        "primary_name": "killer orca"
    },
    "killer_orca": {
        "required_any": ["orca", "killer whale", "orcinus orca"],
        "banned": [
            "humpback", "blue whale", "beluga", "dolphin", "seaworld", "aquarium"
        ],
        "primary_name": "killer orca"
    },
    "mantis_shrimp": {
        "required_any": ["mantis shrimp", "odontodactylus", "stomatopod", "peacock mantis", "stomatopoda"],
        "banned": [
            "praying mantis", "insect", "hand", "leaf", "plant", "garden", "grass",
            "cooking", "recipe", "fried shrimp", "restaurant", "food", "plate"
        ],
        "primary_name": "mantis shrimp"
    },
    "lion": {
        "required_any": ["lion", "lioness", "panthera leo", "african lion"],
        "banned": ["tiger", "leopard", "cheetah", "jaguar", "sea lion", "mountain lion", "cougar"],
        "primary_name": "african lion"
    },
    "tiger": {
        "required_any": ["tiger", "panthera tigris", "bengal tiger", "siberian tiger"],
        "banned": ["lion", "leopard", "cheetah", "jaguar", "cat"],
        "primary_name": "bengal tiger"
    },
    "crocodile": {
        "required_any": ["crocodile", "alligator", "caiman", "crocodylus"],
        "banned": ["lizard", "gecko", "snake", "turtle", "bag", "shoes", "leather"],
        "primary_name": "crocodile"
    },
    "wolf": {
        "required_any": ["wolf", "wolves", "canis lupus", "timber wolf", "gray wolf"],
        "banned": ["dog", "husky", "puppy", "fox", "coyote", "jackal"],
        "primary_name": "gray wolf"
    }
}

def validate_clip_metadata(
    video_title: str,
    video_tags: str,
    target_creature: str,
    target_action: str = ""
) -> Tuple[bool, int, str]:
    """
    Valida y puntúa estrictamente si un video corresponde al animal y acción del guion.
    
    Retorna:
    - (es_valido: bool, score: int, motivo: str)
    """
    text_to_check = f"{video_title} {video_tags}".lower().replace("-", " ").replace("_", " ")
    
    # 1. Comprobar lista negra global (Cero buzos, acuarios, jaulas, caricaturas, personas)
    for banned in GLOBAL_BANNED_WORDS:
        # Usar límite de palabra para evitar falsos positivos
        if re.search(r'\b' + re.escape(banned) + r'\b', text_to_check):
            return False, -100, f"Contiene palabra prohibida global: '{banned}'"

    # 2. Comprobar reglas específicas de la especie
    creature_key = target_creature.lower().replace("-", "_").replace(" ", "_").strip()
    # Buscar regla que coincida
    rule = None
    for k, r in SPECIES_RULES.items():
        if k in creature_key or creature_key in k:
            rule = r
            break

    if not rule:
        # Regla genérica si no está en catálogo específico
        base_name = creature_key.split()[0]
        rule = {
            "required_any": [base_name],
            "banned": ["zoo", "cage", "pet", "cartoon"],
            "primary_name": base_name
        }

    # Comprobar palabras prohibidas específicas de la especie (ej. rechazar tiburón ballena o cigüeña blanca)
    for spec_banned in rule.get("banned", []):
        if re.search(r'\b' + re.escape(spec_banned) + r'\b', text_to_check):
            return False, -100, f"Contiene especie prohibida o contexto incorrecto: '{spec_banned}'"

    # Comprobar que contenga al menos uno de los términos requeridos de la especie
    has_required = False
    matched_term = ""
    for req in rule.get("required_any", []):
        if re.search(r'\b' + re.escape(req) + r'\b', text_to_check):
            has_required = True
            matched_term = req
            break

    if not has_required:
        return False, 0, f"No contiene el nombre requerido de la especie '{rule.get('primary_name')}'"

    # 3. Calcular puntuación de relevancia
    score = 50  # Puntuación base por coincidencia de especie limpia
    
    # Bonificación si el término coincidente es el nombre completo exacto
    if rule.get("primary_name", "") in text_to_check:
        score += 30

    # Bonificación por coincidencia con la acción del guion (ej. "teeth", "hunting", "breach", "eyes")
    if target_action:
        action_words = [w for w in re.findall(r'\b[a-z]{3,}\b', target_action.lower()) if w not in GLOBAL_BANNED_WORDS]
        for act_w in action_words:
            if act_w in text_to_check:
                score += 15

    return True, score, f"Aprobado (Match: '{matched_term}', Score: {score})"
