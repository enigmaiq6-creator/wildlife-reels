from typing import Dict, List, Any

# Mapeo de intenciones visuales por acto narrativo
ACT_INTENTS = {
    1: {"type": "hook_reveal", "suffix": "close up predator cinematic 4k"},
    2: {"type": "scale_weapons", "suffix": "teeth jaws claws weapons scale 4k"},
    3: {"type": "hunt_strike", "suffix": "hunting attack strike speed slow motion 4k"},
    4: {"type": "death_stare", "suffix": "eyes face stare looking camera 4k vertical"},
    5: {"type": "wild_habitat", "suffix": "swimming walking wild habitat nature 4k"},
    6: {"type": "climax_cta", "suffix": "roar open mouth sound dramatic slow motion 4k"}
}

def generate_scene_search_plan(
    creature_name: str,
    act_num: int,
    act_name: str,
    act_text: str,
    num_shots: int
) -> List[Dict[str, Any]]:
    """
    Genera un plan de búsqueda visual detallado para cada toma de la escena
    basado exactamente en lo que dice el guion.
    """
    clean_creature = creature_name.lower().strip()
    act_intent = ACT_INTENTS.get(act_num, {"type": "action", "suffix": "wildlife 4k"})
    
    shots_plan = []
    
    for s_idx in range(num_shots):
        if act_num == 1:
            # Gancho de impacto
            queries = [
                f"{clean_creature} predator cinematic",
                f"{clean_creature} swimming deep blue" if "ocean" in act_text or "shark" in clean_creature else f"{clean_creature} wild rainforest",
                f"{clean_creature} close up"
            ]
            action_desc = "predator_reveal"
        elif act_num == 2:
            # Escala y armas
            if "teeth" in act_text.lower() or "jaw" in act_text.lower():
                queries = [f"{clean_creature} teeth jaws", f"{clean_creature} mouth open", f"{clean_creature} head close up"]
                action_desc = "teeth_jaws"
            elif "claws" in act_text.lower() or "talon" in act_text.lower():
                queries = [f"{clean_creature} talons claws", f"{clean_creature} close up", f"{clean_creature} perched"]
                action_desc = "claws_talons"
            else:
                queries = [f"{clean_creature} massive size", f"{clean_creature} close up", f"{clean_creature} predator"]
                action_desc = "scale_anatomy"
        elif act_num == 3:
            # Cacería y ataque (BAM!)
            if s_idx == 0:
                queries = [f"{clean_creature} stalking hunting", f"{clean_creature} stealth", f"{clean_creature} swimming"]
                action_desc = "stealth_stalking"
            else:
                queries = [f"{clean_creature} attack strike", f"{clean_creature} speed slow motion", f"{clean_creature} hunting"]
                action_desc = "explosive_strike"
        elif act_num == 4:
            # Mirada fija / Conducta
            queries = [f"{clean_creature} eyes staring", f"{clean_creature} face looking camera", f"{clean_creature} close up face"]
            action_desc = "death_stare"
        elif act_num == 5:
            # Hábitat / Movimiento
            queries = [f"{clean_creature} swimming underwater" if "shark" in clean_creature or "orca" in clean_creature else f"{clean_creature} walking jungle", f"{clean_creature} nature habitat"]
            action_desc = "natural_habitat"
        else:
            # Clímax / Llamado a la acción
            queries = [f"{clean_creature} dramatic", f"{clean_creature} open mouth", f"{clean_creature} close up 4k"]
            action_desc = "climax_pose"

        shots_plan.append({
            "shot_index": s_idx,
            "action_desc": action_desc,
            "search_queries": queries
        })

    return shots_plan
