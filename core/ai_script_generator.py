import os
import json
import random
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional

class AIScriptGenerator:
    """
    Generador Autónomo de Guiones de Vida Salvaje con IA (Groq Cloud):
    - Genera guiones documentales 100% en ESPAÑOL sobre fauna, depredadores y supervivencia animal.
    - Soporta tolerancia a fallos con doble clave API (GROQ_API_KEY y GROQ_API_KEY_BACKUP).
    - Conmutación en cascada entre los modelos más veloces y precisos de Groq.
    - Consulta el historial para garantizar CERO REPETICIÓN de especies o temas.
    """

    GROQ_MODELS = [
        "openai/gpt-oss-120b", # Modelo #1 ultra-inteligente y rápido (0.9s)
        "openai/gpt-oss-20b",  # Modelo #2 de alta velocidad (0.6s)
        "groq/compound-mini"   # Modelo #3 respaldo ligero (0.8s)
    ]

    WILDLIFE_NICHES = [
        "Depredadores alfa y cazadores letales de la sabana o la selva",
        "Criaturas abisales y monstruos del océano profundo",
        "Animales con venenos letales y toxinas mortales",
        "Estrategias extremas de supervivencia y camuflaje animal",
        "Aves rapaces y cazadores del cielo con sentidos hipersensibles",
        "Insectos y artrópodos con habilidades biológicas increíbles",
        "Gigantes prehistóricos o especies al borde de la extinción con adaptaciones únicas",
        "Simbiosis y batallas territoriales en la naturaleza salvaje"
    ]

    def __init__(self, primary_key: Optional[str] = None, backup_key: Optional[str] = None):
        k1 = primary_key or os.getenv("GROQ_API_KEY", "")
        k2 = backup_key or os.getenv("GROQ_API_KEY_BACKUP", "")
        
        self.api_keys = [k for k in [k1, k2] if k.strip()]
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate_wildlife_script(self, seen_topics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Genera un guion documental inédito de Vida Salvaje en Español."""
        if not self.api_keys:
            print("[AIScriptGenerator] [!] No se configuraron claves de Groq. Usando catálogo de respaldo.")
            return None

        seen_topics = seen_topics or []
        seen_str = ", ".join(seen_topics[-30:]) if seen_topics else "ninguno"
        selected_niche = random.choice(self.WILDLIFE_NICHES)

        prompt = f"""Eres un biólogo experto y director de documentales estilo National Geographic / BBC Earth.
Tu misión es crear un guion VIRAL para un video corto (Reel de 50-55 segundos) sobre: {selected_niche}.

REGLAS CRÍTICAS:
1. Idioma: 100% ESPAÑOL natural, cautivador, apasionante y cinematográfico.
2. Formato:
   - topic_id: Identificador único en mayúsculas y guiones (ej. 'AGUILA-ARPIA-CAZADORA', 'CALAMAR-COLOSAL-ABISMAL').
   - title: Título atractivo (ej. '5 Secretos Letales del Águila Arpía').
   - hook: Gancho magnético inicial de 2 a 3 segundos (ej. '¡Esta es el águila más poderosa del planeta y caza monos en segundos!').
   - curiosities: Exactamente 5 datos asombrosos y científicamente verificados. Cada dato debe comenzar con 'Número uno:', 'Número dos:', 'Número tres:', 'Número cuatro:', 'Número cinco:'.
   - cta: Llamado a la acción que invite a debatir en comentarios (ej. '¿Crees que este depredador podría vencer a un jaguar? ¡Comenta y síguenos para más vida salvaje!').
   - pexels_keywords: Lista de exactamente 7 términos de búsqueda en INGLÉS para buscar clips de stock 4K de alta calidad (1 para el gancho, 5 para cada curiosidad, 1 para el llamado a la acción). Ej: ['harpy eagle hunting 4k', 'giant eagle talons close up', ...]
   - hashtags: Lista de 6 hashtags virales en español (ej. ['#vidasalvaje', '#animales', '#naturaleza', '#depredadores', '#fauna', '#documental']).
3. EXCLUSIÓN: No repitas ninguno de los siguientes temas ya publicados: [{seen_str}].

Responde ÚNICA Y EXCLUSIVAMENTE con un objeto JSON válido con la siguiente estructura exacta:
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
                    print(f"[AIScriptGenerator] [+] Consultando Groq AI ({model_name}) [Key {key_idx}]...")
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "WildlifeVideoEngine/2.0"
                    }
                    
                    payload = {
                        "model": model_name,
                        "messages": [
                            {"role": "system", "content": "Eres un asistente que responde exclusivamente en JSON válido estructurado."},
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
                        
                        # Validar campos obligatorios
                        req_fields = ["topic_id", "title", "hook", "curiosities", "cta", "pexels_keywords", "hashtags"]
                        if all(f in script_json for f in req_fields) and len(script_json["curiosities"]) == 5:
                            topic_id = script_json["topic_id"].strip().upper().replace(" ", "-")
                            script_json["topic_id"] = topic_id
                            print(f"[AIScriptGenerator] [ÉXITO TOTAL] Tema de Vida Salvaje creado: '{topic_id}' - {script_json['title']}")
                            return script_json
                except Exception as e:
                    print(f"[AIScriptGenerator] [!] Falló {model_name} con Key {key_idx}: {str(e)[:80]}")
                    continue

        return None
