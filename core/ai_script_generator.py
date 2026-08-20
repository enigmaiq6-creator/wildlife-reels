import os
import json
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class AIScriptGenerator:
    """
    Autonomous Wildlife AI Script Generator (Groq Cloud):
    - Generates 100% SIMPLE, CLEAR, AND ENGAGING ENGLISH wildlife scripts.
    - Uses easy-to-understand vocabulary (high retention for global & US viewers).
    - Multi-Key failover support (GROQ_API_KEY and GROQ_API_KEY_BACKUP).
    - 3-tier cascade model fallback.
    - Zero topic repetition via history.json check.
    """

    GROQ_MODELS = [
        "openai/gpt-oss-120b", # Model #1 ultra-fast (0.9s)
        "openai/gpt-oss-20b",  # Model #2 high speed (0.6s)
        "groq/compound-mini"   # Model #3 fallback (0.8s)
    ]

    WILDLIFE_NICHES = [
        "Apex predators and extreme hunters of the savannah, jungle, or arctic",
        "Deep sea ocean monsters and glowing abyss creatures",
        "Deadly venomous animals and secret animal weapons",
        "Extreme survival skills, mimicry, and camouflage in the wild",
        "Eagles, owls, and birds of prey with supersonic vision",
        "Superpowered insects and armored bugs that defy science",
        "Giant animals, apex reptiles, and ancient living fossils",
        "Animal rivalries and territorial battles in nature"
    ]

    def __init__(self, primary_key: Optional[str] = None, backup_key: Optional[str] = None):
        k1 = primary_key or os.getenv("GROQ_API_KEY", "")
        k2 = backup_key or os.getenv("GROQ_API_KEY_BACKUP", "")
        
        self.api_keys = [k for k in [k1, k2] if k.strip()]
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate_wildlife_script(self, seen_topics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Generates a fresh, unseen wildlife documentary script in SIMPLE, EASY-TO-UNDERSTAND ENGLISH."""
        if not self.api_keys:
            print("[AIScriptGenerator] [!] No Groq API keys configured. Using fallback catalog.")
            return None

        seen_topics = seen_topics or []
        seen_str = ", ".join(seen_topics[-30:]) if seen_topics else "none"
        selected_niche = random.choice(self.WILDLIFE_NICHES)

        prompt = f"""You are a master wildlife documentary creator like BBC Earth and National Geographic.
Create a VIRAL, highly engaging short video script (50-55 seconds) about: {selected_niche}.

CRITICAL RULES:
1. Language: 100% SIMPLE, CLEAR, AND EXCITING ENGLISH. Use easy-to-understand words that anyone in the world can enjoy without feeling confused.
2. Structure:
   - topic_id: Unique uppercase slug with dashes (e.g. 'HARPY-EAGLE-MONSTER', 'COLOSSAL-SQUID-MYSTERY').
   - title: Catchy, simple title (e.g. '5 Insane Facts About the World's Deadliest Eagle!').
   - hook: 2-3 second magnetic hook (e.g. 'This massive eagle has talons larger than a grizzly bear!').
   - curiosities: Exactly 5 mind-blowing facts. Each MUST start with 'Number one:', 'Number two:', 'Number three:', 'Number four:', 'Number five:'.
   - cta: Simple call to action prompting comments (e.g. 'Who would win: a Jaguar or an Anaconda? Drop your answer below and follow for more wildlife!').
   - pexels_keywords: List of exactly 7 search terms in English for 4K vertical stock videos (1 for hook, 5 for curiosities, 1 for CTA).
   - hashtags: List of 6 viral English hashtags (e.g. ['#wildlife', '#animals', '#nature', '#predators', '#documentary', '#wild']).
3. EXCLUSION: Do NOT repeat any of these previously published topics: [{seen_str}].

Respond ONLY with a valid JSON object matching this exact schema:
{{
  "topic_id": "STRING",
  "title": "STRING",
  "hook": "STRING",
  "curiosities": ["STRING", "STRING", "STRING", "STRING", "STRING"],
  "cta": "STRING",
  "pexels_keywords": ["STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING"],
  "hashtags": ["STRING", "STRING", "STRING", "STRING", "STRING", "STRING"]
}}"""

        for key_idx, api_key in enumerate(self.api_keys, 1):
            for model_name in self.GROQ_MODELS:
                try:
                    print(f"[AIScriptGenerator] [+] Querying Groq AI ({model_name}) [Key {key_idx}] for simple English script...")
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "WildlifeVideoEngine/2.0"
                    }
                    
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "You are a professional assistant that responds ONLY with valid structured JSON."},
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
                        
                        req_fields = ["topic_id", "title", "hook", "curiosities", "cta", "pexels_keywords", "hashtags"]
                        if all(f in script_json for f in req_fields) and len(script_json["curiosities"]) == 5:
                            topic_id = script_json["topic_id"].strip().upper().replace(" ", "-")
                            script_json["topic_id"] = topic_id
                            print(f"[AIScriptGenerator] [SUCCESS] Created Simple English Wildlife Topic: '{topic_id}' - {script_json['title']}")
                            return script_json
                except Exception as e:
                    print(f"[AIScriptGenerator] [!] Failed {model_name} with Key {key_idx}: {str(e)[:80]}")
                    continue

        return None
