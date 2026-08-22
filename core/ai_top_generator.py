import os
import json
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class AITopGenerator:
    """
    Generador Autónomo de Videos TOP / Cuenta Regresiva (#3, #2, #1) con IA (Groq):
    - Crea guiones de alto impacto y retención viral estilo YouTube Shorts / Pesca Voraz.
    - Estructura de 50-60 segundos:
        - Gancho Inicial (0-5s)
        - #3 (5-20s)
        - #2 (20-35s)
        - #1 (35-50s)
        - Pregunta / CTA de Cierre (50-58s)
    """

    GROQ_MODELS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "groq/compound-mini"
    ]

    TOP_THEMES = [
        "Top 3 Most Terrifying Animal Encounters Caught on Camera",
        "Top 3 Deadliest Rainforest Predators on Earth",
        "Top 3 Deep Ocean Monsters That Stalk the Abyss",
        "Top 3 Animal Strikes That Move Faster Than a Bullet",
        "Top 3 Prehistoric Birds Still Alive Today",
        "Top 3 Animals That Hunt in Complete Silence"
    ]

    def __init__(self, primary_key: Optional[str] = None, backup_key: Optional[str] = None):
        k1 = primary_key or os.getenv("GROQ_API_KEY", "")
        k2 = backup_key or os.getenv("GROQ_API_KEY_BACKUP", "")
        self.api_keys = [k for k in [k1, k2] if k.strip()]
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate_top_script(self, seen_topics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Genera un guion de Top 3 en inglés simple y dinámico."""
        if not self.api_keys:
            print("[AITopGenerator] [!] No hay llaves de Groq configuradas. Usando catálogo de respaldo.")
            return None

        chosen_theme = random.choice(self.TOP_THEMES)

        prompt = f"""You are a master viral video producer creating a TOP 3 COUNTDOWN YouTube Short / Facebook Reel about: '{chosen_theme}'.

VIRAL HOOK & PACING RULES (FIRST 3 SECONDS MUST STOP THE SCROLL):
1. HOOK (0-3 SECONDS):
   - MUST be an immediate curiosity-gap hook that forces the viewer to stay until #1.
   - Example 1: "These three creatures possess abilities so terrifying, scientists couldn't believe they were real."
   - Example 2: "Whatever you do, NEVER get close to number one on this list."
   - Example 3: "Number one on this list has a strike that literally shatters bulletproof glass."
2. STRUCTURE:
   - hook: 1 punchy curiosity-gap sentence opening the countdown (0-3s).
   - items: EXACTLY 3 items in descending order (#3, #2, #1).
     Each item must contain:
     - rank: integer (3, 2, or 1)
     - badge: string like '#3: THE [BADGE NAME]' (e.g. '#3: THE DINOSAUR BIRD')
     - creature_name: the specific animal (e.g. 'shoebill stork', 'jaguar', 'great white shark', 'harpy eagle', 'orca', 'mantis shrimp')
     - text: 2 dramatic sentences starting with 'Number [three/two/one]: The [Animal Name]...' describing its shocking trait or attack.
     - action_type: one of ('predator_reveal', 'teeth_jaws', 'stealth_stalking', 'explosive_strike', 'death_stare_eyes', 'wild_habitat')
   - climax_cta: 1 closing question asking viewers which one was the most terrifying and to follow Wild Vault.
   - hashtags: 6 viral hashtags (e.g. ['#wildvault', '#wildlife', '#animals', '#top3', '#predators', '#nature']).

Respond ONLY with valid JSON matching this schema:
{{
  "topic_id": "TOP_SLUG",
  "title": "CATCHY_TITLE",
  "hook": "STRING",
  "items": [
    {{
      "rank": 3,
      "badge": "#3: BADGE",
      "creature_name": "ANIMAL",
      "text": "STRING",
      "action_type": "ACTION"
    }},
    {{
      "rank": 2,
      "badge": "#2: BADGE",
      "creature_name": "ANIMAL",
      "text": "STRING",
      "action_type": "ACTION"
    }},
    {{
      "rank": 1,
      "badge": "#1: BADGE",
      "creature_name": "ANIMAL",
      "text": "STRING",
      "action_type": "ACTION"
    }}
  ],
  "climax_cta": "STRING",
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5", "#tag6"]
}}"""

        for key_idx, api_key in enumerate(self.api_keys, 1):
            for model_name in self.GROQ_MODELS:
                try:
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "WildlifeTopEngine/2.0"
                    }
                    data = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "You are a specialized viral countdown video scriptwriter. Output JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800,
                        "response_format": {"type": "json_object"}
                    }
                    req = urllib.request.Request(self.endpoint, data=json.dumps(data).encode('utf-8'), headers=headers)
                    with urllib.request.urlopen(req, timeout=12) as response:
                        res = json.loads(response.read().decode('utf-8'))
                        raw_json = res['choices'][0]['message']['content']
                        parsed = json.loads(raw_json)
                        if "items" in parsed and len(parsed["items"]) == 3:
                            print(f"[AITopGenerator] [+] Guion Top 3 generado con éxito: '{parsed.get('title')}'")
                            return parsed
                except Exception as e:
                    continue

        return None
