import os
import time
import json
import base64
import urllib.parse
import urllib.request
import requests
from pathlib import Path
from typing import Optional
from google.oauth2 import service_account
import google.auth.transport.requests

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = BASE_DIR / "credentials" / "gcp_service_account.json"
CACHE_DIR = BASE_DIR / "assets" / "image_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

class GCPVertexImageGenerator:
    """
    Generador de Imágenes Inteligente con Optimización Extrema de Costos y Créditos:
    1. Tier 1 (Costo $0): Busca fotos reales en Pexels 4K / Wikimedia Commons si es una especie viva.
    2. Tier 2 (Créditos Google Cloud): Invoca Vertex AI (facebookbot-502117) para escenas inéditas,
       híbridos, prehistoria y cuando no hay stock gratuito.
    3. Tier 3 (Costo $0): Respaldo IA gratuito de alta definición (Pollinations Flux).
    """

    _creds = None
    _token = None
    _project_id = "facebookbot-502117"
    _location = "us-central1"
    _used_photo_urls = set()

    @classmethod
    def _get_auth_token(cls) -> Optional[str]:
        try:
            if not CREDENTIALS_PATH.exists():
                return None
            if cls._creds is None:
                cls._creds = service_account.Credentials.from_service_account_file(
                    str(CREDENTIALS_PATH),
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
            auth_req = google.auth.transport.requests.Request()
            cls._creds.refresh(auth_req)
            cls._token = cls._creds.token
            return cls._token
        except Exception as e:
            print(f"[GCPVertexAI] Error obteniendo token de autenticación: {e}")
            return None

    @classmethod
    def reset_session(cls):
        cls._used_photo_urls.clear()

    @classmethod
    def _search_free_stock_photo(cls, query_prompt: str, output_path: Path) -> bool:
        """
        Tier 1 (Ahorro Máximo - $0 Costo):
        Descarga fotos profesionales de Pexels 4K o Wikimedia garantizando CERO FOTOS REPETIDAS.
        """
        # Si el prompt es de animales extintos o anime, saltar a Vertex AI
        forbidden_stock = ["prehistoric", "extinct", "anime", "illustration", "hybrid", "transparent head", "drawing", "glowing eyes"]
        if any(w in query_prompt.lower() for w in forbidden_stock):
            return False

        # Limpiar palabras clave para búsqueda de stock
        clean_q = query_prompt.replace("isolated", "").replace("studio portrait", "").replace("black background", "").replace("white background", "").strip()
        
        # 1. Pexels Photo API con selección de fotos inéditas
        pexels_key = os.environ.get("PEXELS_API_KEY", "")
        if pexels_key:
            try:
                p_url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(clean_q)}&per_page=15&orientation=portrait"
                p_resp = requests.get(p_url, headers={"Authorization": pexels_key}, timeout=8)
                if p_resp.status_code == 200:
                    photos = p_resp.json().get("photos", [])
                    # Filtrar fotos no usadas en esta sesión
                    unused_photos = [p for p in photos if (p.get("src", {}).get("large2x") or p.get("src", {}).get("large")) not in cls._used_photo_urls]
                    if unused_photos:
                        chosen_photo = random.choice(unused_photos[:5])
                        img_url = chosen_photo.get("src", {}).get("large2x") or chosen_photo.get("src", {}).get("large")
                        if img_url:
                            img_data = requests.get(img_url, timeout=12).content
                            if len(img_data) > 10000:
                                cls._used_photo_urls.add(img_url)
                                output_path.write_bytes(img_data)
                                print(f"[GCPVertexAI] [FOTO 4K INÉDITA #{len(cls._used_photo_urls)}] Pexels -> {output_path.name}")
                                return True
            except Exception:
                pass

        return False

    @classmethod
    def _fallback_generate(cls, prompt: str, output_path: Path) -> bool:
        """
        Tier 3 (Costo $0): Generador IA de respaldo si Vertex AI no está disponible.
        """
        clean_prompt = f"National geographic photography of {prompt}, high detail 4k award winning wildlife photo, studio lighting"
        encoded_prompt = urllib.parse.quote(clean_prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1350&nologo=true&seed={int(time.time()*1000)%100000}"
        
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
                if len(data) > 10000:
                    output_path.write_bytes(data)
                    print(f"[GCPVertexAI] [+] Imagen generada vía Respaldo IA Gratuito -> {output_path.name}")
                    return True
        except Exception as e:
            print(f"[GCPVertexAI] [!] Error en respaldo gratuito: {e}")

        return False

    @classmethod
    def generate_image(
        cls,
        prompt: str,
        output_path: Path,
        prefer_free_stock: bool = True
    ) -> bool:
        """
        Genera una fotografía fotorrealista de alta definición optimizando al máximo los créditos de Google Cloud.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 1. Intentar obtener foto gratuita en Tier 1 para ahorrar créditos
        if prefer_free_stock:
            if cls._search_free_stock_photo(prompt, output_path):
                return True

        # 2. Tier 2: Usar Google Cloud Vertex AI (facebookbot-502117)
        token = cls._get_auth_token()
        if token:
            url = f"https://{cls._location}-aiplatform.googleapis.com/v1beta1/projects/{cls._project_id}/locations/{cls._location}/publishers/google/models/gemini-2.5-flash-image:generateContent"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8"
            }

            cinematic_prompt = (
                f"National Geographic photorealistic vertical 4k wildlife photography of {prompt}. "
                f"Award winning wildlife documentary photo, 8k resolution, volumetric natural lighting, razor sharp focus, high contrast."
            )

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [{"text": cinematic_prompt}]
                    }
                ],
                "generationConfig": {
                    "responseModalities": ["IMAGE"]
                }
            }

            print(f"[GCPVertexAI] [GENERANDO CON CRÉDITOS GOOGLE CLOUD] '{prompt[:50]}...'")

            for attempt in range(2):
                try:
                    resp = requests.post(url, headers=headers, json=payload, timeout=35)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                inline_data = part.get("inlineData", {})
                                b64_data = inline_data.get("data")
                                if b64_data:
                                    img_bytes = base64.b64decode(b64_data)
                                    output_path.write_bytes(img_bytes)
                                    print(f"[GCPVertexAI] [IMAGEN GOOGLE CLOUD GENERADA] ({len(img_bytes)} bytes) -> {output_path.name}")
                                    return True
                    elif resp.status_code == 429:
                        time.sleep(2)
                        continue
                    else:
                        break
                except Exception:
                    break

        # 3. Tier 3: Si Vertex AI falló o alcanzó límite, usar respaldo gratuito
        return cls._fallback_generate(prompt, output_path)
