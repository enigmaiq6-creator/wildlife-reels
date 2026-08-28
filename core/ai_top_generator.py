import os
import json
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class AITopGenerator:
    """
    Generador Autónomo de Videos TOP / Cuenta Regresiva (#3, #2, #1) con IA (Groq):
    - Crea guiones de alto impacto y retención viral estilo YouTube Shorts / Pesca Voraz.
    - Cuenta con más de 50 temáticas distintas y control estricto de no-repetición de animales.
    """

    GROQ_MODELS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
        "groq/compound-mini"
    ]

    TOP_THEMES = [
        "Top 3 Most Lethal Venomous Animals in the World",
        "Top 3 Deep Ocean Monsters That Stalk the Abyss",
        "Top 3 Animal Strikes That Move Faster Than a Bullet",
        "Top 3 Prehistoric Birds and Beasts Still Alive Today",
        "Top 3 Predators That Hunt in Complete Absolute Silence",
        "Top 3 Most Fearless Animals That Never Back Down",
        "Top 3 River Monsters with Terrifying Jaws",
        "Top 3 Microscopic Killers with Deadly Superpowers",
        "Top 3 Animals with the Highest Bite Force on Earth",
        "Top 3 Masters of Camouflage You Will Never See Coming",
        "Top 3 Arctic Apex Hunters Surviving Sub-Zero Temperatures",
        "Top 3 Deadly Creatures with Incurable Neurotoxins",
        "Top 3 Aerial Assassins That Dive at Extreme Speeds",
        "Top 3 Rainforest Predators with Night Vision",
        "Top 3 Animals That Can Produce Lethal Electric Shocks or Heat",
        "Top 3 Ocean Monsters with Glowing Bioluminescent Traps",
        "Top 3 Desert Survival Monsters That Never Drink Water",
        "Top 3 Insect Swarms Capable of Taking Down Giant Prey",
        "Top 3 Underwater Ambushes Caught on High Speed Cameras",
        "Top 3 Living Fossils That Outlived the Dinosaurs",
        "Top 3 Pack Hunters with the Highest Kill Success Rates",
        "Top 3 Creatures with Bulletproof Armor and Natural Shields",
        "Top 3 Cave-Dwelling Predators That Hunt in Pitch Black",
        "Top 3 Animals with Weaponized Tails and Venomous Stingers",
        "Top 3 Bizarre Creatures That Look Like Extraterrestrial Aliens"
    ]

    DIVERSE_CREATURE_POOL = [
        "Inland Taipan", "Pistol Shrimp", "Honey Badger", "Peregrine Falcon",
        "Box Jellyfish", "Golden Poison Frog", "Electric Eel", "Blue-Ringed Octopus",
        "Orca", "Wolverine", "Cassowary", "Cone Snail", "Nile Crocodile",
        "Bull Shark", "Goblin Shark", "Driver Ants", "Sydney Funnel-Web Spider",
        "Deathstalker Scorpion", "Barreleye Fish", "Harpy Eagle", "Komodo Dragon",
        "Shoebill Stork", "Mantis Shrimp", "Jaguar", "Great White Shark",
        "African Crowned Eagle", "Siberian Tiger", "Goliath Tigerfish", "Vampire Bat",
        "Giant Freshwater Stingray", "Alligator Snapping Turtle", "Tarantula Hawk Wasp",
        "Secretary Bird", "Bearded Vulture", "Hammerhead Shark", "Moray Eel",
        "Giant Anteater", "Stonefish", "Black Mamba", "King Cobra", "Green Anaconda",
        "Snow Leopard", "Leopard Seal", "Colossal Squid", "Osprey", "Grizzly Bear"
    ]

    def __init__(self, primary_key: Optional[str] = None, backup_key: Optional[str] = None):
        k1 = primary_key or os.getenv("GROQ_API_KEY", "")
        k2 = backup_key or os.getenv("GROQ_API_KEY_BACKUP", "")
        self.api_keys = [k for k in [k1, k2] if k.strip()]
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate_top_script(self, seen_topics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Genera un guion de Top 3 en inglés simple, dinámico y 100% fresco."""
        if not self.api_keys:
            print("[AITopGenerator] [!] No hay llaves de Groq configuradas. Usando catálogo de respaldo.")
            return None

        seen_topics = seen_topics or []
        seen_str = ", ".join(seen_topics[-30:]) if seen_topics else "none"

        # Filtrar temáticas vistas
        available_themes = [
            t for t in self.TOP_THEMES
            if not any(w in [s.lower() for s in seen_topics] for w in t.lower().split() if len(w) > 4)
        ]
        if not available_themes:
            available_themes = self.TOP_THEMES

        chosen_theme = random.choice(available_themes)
        suggested_sample = random.sample(self.DIVERSE_CREATURE_POOL, 8)

        prompt = f"""You are an elite viral nature video director producing a TOP 3 COUNTDOWN YouTube Short / Facebook Reel.
THEME: '{chosen_theme}'.

MANDATORY ANTI-REPETITION RULES:
1. DO NOT REPEAT previously featured species: [{seen_str}].
2. Choose 3 COMPLETELY DISTINCT creatures fitting the theme from diverse global fauna (Suggested options: {", ".join(suggested_sample)}).
3. The first 3 seconds (HOOK) must be unique and directly tease the terrifying nature of #1.

STRUCTURE:
- hook: 1 punchy curiosity-gap sentence opening the countdown (0-3s).
- items: EXACTLY 3 items in descending order (#3, #2, #1).
  Each item must contain:
  - rank: integer (3, 2, or 1)
  - badge: string like '#3: THE [BADGE NAME]' (e.g. '#3: THE 5000-VOLT ASSASSIN')
  - creature_name: the specific animal name in English (e.g. 'electric eel', 'inland taipan', 'honey badger')
  - text: 2 dramatic sentences starting with 'Number [three/two/one]: The [Animal Name]...' describing its shocking trait or attack.
  - action_type: one of ('predator_reveal', 'teeth_jaws', 'stealth_stalking', 'explosive_strike', 'death_stare_eyes', 'wild_habitat')
- climax_cta: 1 closing question asking viewers which one was the most terrifying and to follow Wild Vault.
- hashtags: 6 viral hashtags (e.g. ['#wildvault', '#wildlife', '#animals', '#top3', '#predators', '#nature']).

Respond ONLY with valid JSON matching this schema:
{{
  "topic_id": "TOP_UNIQUE_SLUG",
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
                            {"role": "system", "content": "You are a specialized viral countdown video scriptwriter. Output strictly valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.75,
                        "max_tokens": 2048,
                        "response_format": {"type": "json_object"}
                    }
                    req = urllib.request.Request(self.endpoint, data=json.dumps(data).encode('utf-8'), headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        res = json.loads(response.read().decode('utf-8'))
                        raw_json = res['choices'][0]['message']['content']
                        parsed = json.loads(raw_json)
                        if "items" in parsed and len(parsed["items"]) == 3:
                            print(f"[AITopGenerator] [+] Guion Top 3 generado con éxito: '{parsed.get('title')}'")
                            return parsed
                except Exception as e:
                    print(f"[AITopGenerator] [!] Error con modelo {model_name} (Key {key_idx}): {e}")
                    continue

        return None
