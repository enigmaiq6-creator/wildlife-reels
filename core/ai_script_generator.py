import os
import json
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class AIScriptGenerator:
    """
    Autonomous Wildlife Micro-Documentary AI Generator (Ares G Style):
    - Creates 45-second cinematic single-creature suspense stories (NO 5-fact listicles).
    - 6-Act Storytelling Arc:
        Act 1: Shock / Jurassic Hook (0-3s)
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
        "Peregrine Falcon (The 240 MPH Sky Missile)"
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
        chosen_creature = random.choice(self.CREATURE_CANDIDATES)

        prompt = f"""You are a master viral nature documentary filmmaker (style: BBC Earth, Ares G, Nat Geo Wild).
Create a VIRAL, ultra-suspenseful 45-second MICRO-DOCUMENTARY script about ONE single creature: {chosen_creature}.

CRITICAL VIRAL HOOK & PACING RULES (FIRST 3 SECONDS MUST STOP THE SCROLL):
1. ACT 1 (THE 3-SECOND VIRAL HOOK):
   - MUST be an INSTANT CURIOSITY TRAP that makes it impossible to scroll away.
   - BANNED CLICHES: Do NOT start with 'Did you know', 'What if I told you', 'Meet the...', or 'In the wild'.
   - USE ONE OF THESE 4 PROVEN VIRAL HOOK FORMULAS:
     a) The Forbidden Warning: "Whatever you do, NEVER look this creature in the eyes if you encounter it..."
     b) The Impossible Fact: "This animal is officially banned from public aquariums because it can literally shatter bulletproof glass..."
     c) The Survival Threat: "If you ever hear this bizarre sound in the rainforest, you have three seconds to run..."
     d) The Mind-Bending Mystery: "Scientists were terrified when they first examined the jaw of this ancient predator..."
2. NARRATIVE FLOW (Continuous 45s story, NOT a listicle):
   - act1_hook: 1 punchy curiosity-gap sentence (0-3s).
   - act2_scale: 1-2 sentences. Terrifying physical scale, weapons, and anatomy (3-9s).
   - act3_hunt: 2 sentences. The stealth stalking and sudden explosive predatory strike (9-20s).
   - act4_behavior: 1-2 sentences. Bizarre psychological trait, death stare, or unique superpower (20-28s).
   - act5_twist: 1-2 sentences. Surprising reality, rare vulnerability, or secret adaptation (28-36s).
   - act6_climax_cta: 1-2 sentences. Sensory climax & provocative question asking the viewer to comment (36-45s).
3. LANGUAGE: Simple, dramatic, impactful English (A2/B1 level). Clear, punchy, cinematic.
4. pexels_keywords: EXACTLY 6 varied action visual search queries for this exact creature (extreme close up eyes, predatory strike, stalking in wild, full body scale, teeth/claws, natural habitat).
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
                    print(f"[AIScriptGenerator] [+] Generating Micro-Doc ({model_name}) [Key {key_idx}]...")
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "WildlifeVideoEngine/2.0"
                    }
                    
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "You are a professional documentary scriptwriter that outputs valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.75,
                        "response_format": {"type": "json_object"}
                    }
                    
                    req = urllib.request.Request(self.endpoint, data=json.dumps(payload).encode("utf-8"), headers=headers)
                    with urllib.request.urlopen(req, timeout=15) as response:
                        res_data = json.loads(response.read().decode("utf-8"))
                        content_str = res_data["choices"][0]["message"]["content"]
                        script_json = json.loads(content_str)
                        
                        req_fields = ["topic_id", "title", "act1_hook", "act2_scale", "act3_hunt", "act4_behavior", "act5_twist", "act6_climax_cta", "pexels_keywords", "hashtags"]
                        if all(f in script_json for f in req_fields):
                            topic_id = script_json["topic_id"].strip().upper().replace(" ", "-")
                            script_json["topic_id"] = topic_id
                            print(f"[AIScriptGenerator] [SUCCESS] Created Micro-Doc: '{topic_id}' - {script_json['title']}")
                            return script_json
                except Exception as e:
                    print(f"[AIScriptGenerator] [!] Failed {model_name} with Key {key_idx}: {str(e)[:80]}")
                    continue

        return None
