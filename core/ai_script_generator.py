import os
import json
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class AIScriptGenerator:
    """
    Autonomous Wildlife Micro-Documentary AI Generator (Ares G Style):
    - Creates 45-second cinematic single-creature suspense stories (NO 5-fact listicles).
    - 6-Act Storytelling Arc:
        Act 1: Shock / Jurassic Hook (0-3s) - Rotating 5 distinct psychological hooks.
        Act 2: Physical Monster Scale & Weapons (3-9s)
        Act 3: The Terrifying Stealth & Strike Mechanism (9-20s) with sudden impact word (BAM!)
        Act 4: Bizarre Psychological Trait / Death Stare (20-28s)
        Act 5: Surprising Twist & Vulnerability (28-36s)
        Act 6: Sensory Climax & Cliffhanger (36-45s)
    - 100% focused on ONE specific apex predator / creature with 6 varied camera angles.
    """

    GROQ_MODELS = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
        "groq/compound-mini"
    ]

    CREATURE_CANDIDATES = [
        "Shoebill Stork (The Prehistoric Dinosaur Bird)",
        "Harpy Eagle (The Monkey-Hunting Giant Raptor)",
        "Mantis Shrimp (The Ocean's Fastest Sonic Punch)",
        "Inland Taipan (The World's Most Lethal Venomous Snake)",
        "Colossal Squid (The Deep Abyss Monster with Rotating Hooks)",
        "Jaguar (The Armor-Crushing River Phantom)",
        "Cassowary (The Living Velociraptor of the Rainforest)",
        "Cone Snail (The Underwater Hypodermic Assassin)",
        "Pistol Shrimp (The Creature That Creates 5000 Degree Plasma Bubbles)",
        "Komodo Dragon (The Island Behemoth with Serrated Teeth)",
        "Great White Shark (The Apex Ocean Torpedo)",
        "Blue-Ringed Octopus (The Glowing Miniature Killer)",
        "Osprey (The Precision Dive Bomber of the Lakes)",
        "Peregrine Falcon (The 240 MPH Sky Missile)",
        "Honey Badger (The Fearless Armor-Plated Brawler)",
        "Wolverine (The Arctic Ghost Predator)",
        "Grizzly Bear (The Alaskan Salmon Smasher)",
        "Siberian Tiger (The Frozen Forest Monarch)",
        "African Crowned Eagle (The Baboon Hunter)",
        "Electric Eel (The 860-Volt River Generator)",
        "Barreleye Fish (The Transparent-Headed Ocean Mystery)",
        "Goblin Shark (The Slingshot Jaw Monster)",
        "Green Anaconda (The Amazon River Constrictor)",
        "Black Mamba (The Coffin-Headed Speed Assassin)",
        "King Cobra (The Snake-Eating Giant Sovereign)",
        "Golden Poison Dart Frog (The 2-Microgram Lethal Jewel)",
        "Stonefish (The Camouflaged Marine Mine)",
        "Box Jellyfish (The 60-Tentacle Ocean Ghost)",
        "Orca (The Antarctic Apex Pack Hunter)",
        "Snow Leopard (The Ghost of the Himalayas)",
        "Leopard Seal (The Antarctic Ice Juggernaut)",
        "Nile Crocodile (The 5000-PSI Bone Crusher)",
        "Bull Shark (The Freshwater River Marauder)",
        "Alligator Snapping Turtle (The Prehistoric River Trap)",
        "Vampire Bat (The Silent Blood Stalker)",
        "Deathstalker Scorpion (The Desert Neurotoxin Stinger)",
        "Sydney Funnel-Web Spider (The Armored Fang Arachnid)",
        "Tarantula Hawk Wasp (The Paralyzing Spider Slayer)",
        "Driver Ant Colony (The Marching Living Lawn Mower)",
        "African Wild Dog (The 90-Percent Success Rate Pack)",
        "Secretary Bird (The Snake-Stomping Martial Raptor)",
        "Bearded Vulture (The Bone-Eating Mountain Giant)",
        "Giant Freshwater Stingray (The Mud-Dwelling River Giant)",
        "Hammerhead Shark (The 360-Degree Electro-Sensor Predator)",
        "Moray Eel (The Double-Jawed Reef Stalker)",
        "Goliath Tigerfish (The Monster with Crocodile Teeth)",
        "Giant Anteater (The Bear-Killing Clawed Phantom)"
    ]

    def __init__(self, primary_key: Optional[str] = None, backup_key: Optional[str] = None):
        k1 = primary_key or os.getenv("GROQ_API_KEY", "")
        k2 = backup_key or os.getenv("GROQ_API_KEY_BACKUP", "")
        self.api_keys = [k for k in [k1, k2] if k.strip()]
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate_wildlife_script(self, seen_topics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Generates a 45-second cinematic micro-documentary script in Simple English."""
        if not self.api_keys:
            print("[AIScriptGenerator] [!] No Groq API keys configured. Using fallback catalog.")
            return None

        seen_topics = seen_topics or []
        seen_str = ", ".join(seen_topics[-30:]) if seen_topics else "none"

        # 1. Cargar historial y extraer especies publicadas recientemente (últimos 35 temas)
        history_file = Path("history.json")
        entries = []
        if history_file.exists():
            try:
                with open(history_file, "r", encoding="utf-8") as f:
                    entries = json.load(f).get("published_topics", [])
            except Exception:
                pass

        recent_entries = entries[-35:] if len(entries) >= 35 else entries
        recent_text = " ".join([
            str(e.get("title", "")) + " " + str(e.get("topic_id", "")) + " " + str(e.get("creature_name", ""))
            for e in recent_entries
        ]).lower()

        # 2. Filtrar candidatos de CREATURE_CANDIDATES que NO aparezcan en los últimos 35 publicados
        available_candidates = []
        for c in self.CREATURE_CANDIDATES:
            main_name = c.split("(")[0].strip().lower()
            if main_name not in recent_text and not any(p in recent_text for p in main_name.split() if len(p) > 4):
                available_candidates.append(c)

        if not available_candidates:
            recent_10_text = " ".join([
                str(e.get("title", "")) + " " + str(e.get("topic_id", ""))
                for e in entries[-10:]
            ]).lower()
            available_candidates = [
                c for c in self.CREATURE_CANDIDATES
                if c.split("(")[0].strip().lower() not in recent_10_text
            ]

        chosen_creature = random.choice(available_candidates) if available_candidates else random.choice(self.CREATURE_CANDIDATES)
        print(f"[AIScriptGenerator] [+] Especie seleccionada para micro-doc (Disponibles frescos: {len(available_candidates)}/{len(self.CREATURE_CANDIDATES)}): '{chosen_creature}'", flush=True)

        hook_styles = [
            "Forbidden Warning (Whatever you do, NEVER...)",
            "Impossible Biology (Scientists still cannot explain how...)",
            "Survival Threat (If you ever hear or spot this, you have three seconds...)",
            "Mind-Bending Scale (It looks harmless until you see what it does to...)",
            "Hidden Assassin (You could walk past it ten times and never realize...)"
        ]
        chosen_hook_style = random.choice(hook_styles)

        prompt = f"""You are a master viral nature documentary filmmaker (style: BBC Earth, Ares G, Nat Geo Wild).
Create a 100% UNIQUE, VIRAL, ultra-suspenseful 45-second MICRO-DOCUMENTARY script about: {chosen_creature}.

CHOSEN VIRAL HOOK FORMULA FOR SCENE 1 (0-3s):
Style: '{chosen_hook_style}'
The very first sentence MUST use this exact psychological angle to hook the viewer instantly with zero fluff or greetings.

CRITICAL PACING & STORYTELLING RULES:
1. ACT 1 (THE 3-SECOND VIRAL HOOK):
   - MUST be an INSTANT CURIOSITY TRAP tailored to '{chosen_hook_style}'.
   - BANNED CLICHES: Do NOT start with 'Did you know', 'What if I told you', 'Meet the...', or 'In the wild'.
2. NARRATIVE FLOW (Continuous 45s story, NOT a listicle):
   - act1_hook: 1 punchy curiosity-gap sentence (0-3s).
   - act2_scale: 1-2 sentences. Terrifying physical scale, weapons, and anatomy (3-9s).
   - act3_hunt: 2 sentences. The stealth stalking and sudden explosive predatory strike (9-20s).
   - act4_behavior: 1-2 sentences. Bizarre psychological trait, death stare, or unique superpower (20-28s).
   - act5_twist: 1-2 sentences. Surprising reality, rare vulnerability, or secret adaptation (28-36s).
   - act6_climax_cta: 1-2 sentences. Sensory climax & provocative question asking the viewer to comment (36-45s).
3. LANGUAGE: Simple, dramatic, impactful English (A2/B1 level). Clear, punchy, cinematic.
4. pexels_keywords: EXACTLY 6 varied action visual search queries for this exact creature:
   - query 1 (Hook): Extreme close-up face/eyes predatory gaze.
   - query 2 (Scale): Full body anatomical size/claws/fangs.
   - query 3 (Hunt): Ambush stalking/creeping in natural habitat.
   - query 4 (Strike): Explosive high-speed attack or strike.
   - query 5 (Detail): Unique body armor or glowing feature.
   - query 6 (Climax): Dramatic slow-motion hero shot.
5. hashtags: 6 viral hashtags (e.g. ['#wildlife', '#animals', '#nature', '#predators', '#documentary', '#wildvault']).
6. EXCLUSION: Do NOT repeat any previously seen topic slugs: [{seen_str}].

Respond ONLY with valid JSON matching this schema:
{{
  "topic_id": "STRING_SLUG",
  "title": "STRING_TITLE",
  "creature_name": "STRING",
  "act1_hook": "STRING",
  "act2_scale": "STRING",
  "act3_hunt": "STRING",
  "act4_behavior": "STRING",
  "act5_twist": "STRING",
  "act6_climax_cta": "STRING",
  "pexels_keywords": ["STRING", "STRING", "STRING", "STRING", "STRING", "STRING"],
  "hashtags": ["STRING", "STRING", "STRING", "STRING", "STRING", "STRING"]
}}"""

        for key_idx, api_key in enumerate(self.api_keys, 1):
            for model_name in self.GROQ_MODELS:
                try:
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "You are an award-winning wildlife documentary scriptwriter. Always return strictly valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.75,
                        "max_tokens": 2048,
                        "response_format": {"type": "json_object"}
                    }

                    data = json.dumps(payload).encode("utf-8")
                    req = urllib.request.Request(
                        self.endpoint,
                        data=data,
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json",
                            "User-Agent": "WildVault-AIScriptEngine/2.0"
                        }
                    )

                    with urllib.request.urlopen(req, timeout=15) as response:
                        result = json.loads(response.read().decode("utf-8"))
                        content = result["choices"][0]["message"]["content"].strip()
                        script_data = json.loads(content)

                        # Validación básica de estructura
                        required_keys = ["topic_id", "title", "act1_hook", "act2_scale", "act3_hunt", "act4_behavior", "act5_twist", "act6_climax_cta", "pexels_keywords"]
                        if all(k in script_data for k in required_keys):
                            safe_t = str(script_data.get('title', '')).encode('ascii', 'ignore').decode()
                            safe_id = str(script_data.get('topic_id', '')).encode('ascii', 'ignore').decode()
                            print(f"[AIScriptGenerator] [SUCCESS] Created Micro-Doc ({chosen_hook_style}): '{safe_id}' - {safe_t}", flush=True)
                            return script_data

                except Exception as e:
                    print(f"[AIScriptGenerator] [!] Error con modelo {model_name} (Key {key_idx}): {e}", flush=True)
                    if "429" in str(e):
                        import time
                        time.sleep(2)
                    continue

        # Respaldo con Google Gemini si está configurado
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip() or os.getenv("GEMINI_API_KEY_2", "").strip()
        if gemini_key:
            print("[AIScriptGenerator] [+] Intentando generacion con Google Gemini API...", flush=True)
            for g_model in ["gemini-1.5-flash", "gemini-2.0-flash"]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{g_model}:generateContent?key={gemini_key}"
                    headers = {"Content-Type": "application/json"}
                    payload = {
                        "contents": [
                            {"role": "user", "parts": [{"text": f"You are an award-winning wildlife documentary scriptwriter. Always return strictly valid JSON.\n\n{prompt}"}]}
                        ],
                        "generationConfig": {
                            "responseMimeType": "application/json",
                            "temperature": 0.8
                        }
                    }
                    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
                    with urllib.request.urlopen(req, timeout=25) as resp:
                        res_data = json.loads(resp.read().decode("utf-8"))
                        text_resp = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        script_data = json.loads(text_resp)
                        required_keys = ["topic_id", "title", "act1_hook", "act2_scale", "act3_hunt", "act4_behavior", "act5_twist", "act6_climax_cta", "pexels_keywords"]
                        if all(k in script_data for k in required_keys):
                            print(f"[AIScriptGenerator] [SUCCESS GEMINI] Created Micro-Doc: '{script_data['topic_id']}' - {script_data['title']}", flush=True)
                            return script_data
                except Exception as ge:
                    print(f"[AIScriptGenerator] [!] Fallo Gemini {g_model}: {ge}", flush=True)

        return None
