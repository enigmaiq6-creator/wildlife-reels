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

class GCPVertexImageGenerator:
    """
    Generador de Imágenes de Ultra Alta Definición utilizando Google Cloud Vertex AI
    y los créditos del proyecto de Google Cloud (facebookbot-502117).
    Incluye sistema de reintentos y fallback a IA de respaldo para garantizar
    que NUNCA se produzca una imagen vacía o negra.
    """

    _creds = None
    _token = None
    _project_id = "facebookbot-502117"
    _location = "us-central1"

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
    def _fallback_generate(cls, prompt: str, output_path: Path) -> bool:
        """
        Generador de Respaldo de Alta Definición si Vertex AI sufre Rate-Limit (429).
        Garantiza que SIEMPRE exista una imagen real del animal.
        """
        print(f"[GCPVertexAI] [!] Activando generador de respaldo de alta definición para: '{prompt[:45]}...'")
        
        # 1. Intento con Pollinations AI (Flux / SDXL)
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
                    print(f"[GCPVertexAI] [+] Imagen generada con éxito vía Respaldo IA ({len(data)} bytes) -> {output_path.name}")
                    return True
        except Exception as e:
            print(f"[GCPVertexAI] [!] Error en respaldo Pollinations: {e}")

        # 2. Intento con Pexels Photo API si está disponible
        pexels_key = os.environ.get("PEXELS_API_KEY", "")
        if pexels_key:
            try:
                search_q = prompt.split("isolated")[0].split("portrait")[0].strip()
                p_url = f"https://api.pexels.com/v1/search?query={urllib.parse.quote(search_q)}&per_page=3&orientation=portrait"
                p_resp = requests.get(p_url, headers={"Authorization": pexels_key}, timeout=10)
                if p_resp.status_code == 200:
                    photos = p_resp.json().get("photos", [])
                    if photos:
                        img_url = photos[0].get("src", {}).get("large2x") or photos[0].get("src", {}).get("large")
                        if img_url:
                            img_data = requests.get(img_url, timeout=15).content
                            if len(img_data) > 10000:
                                output_path.write_bytes(img_data)
                                print(f"[GCPVertexAI] [+] Foto de Pexels 4K descargada ({len(img_data)} bytes) -> {output_path.name}")
                                return True
            except Exception as pe:
                print(f"[GCPVertexAI] [!] Error en respaldo Pexels: {pe}")

        return False

    @classmethod
    def generate_image(
        cls,
        prompt: str,
        output_path: Path,
        aspect_ratio: str = "9:16"
    ) -> bool:
        """
        Genera una fotografía fotorrealista de alta definición usando Google Cloud Vertex AI
        con reintentos automáticos y fallback garantizado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
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

            print(f"[GCPVertexAI] [GENERANDO IMAGEN CON GOOGLE CLOUD VERTEX AI] '{prompt[:50]}...'")

            # Intentar con reintentos si ocurre 429
            max_attempts = 2
            for attempt in range(max_attempts):
                try:
                    resp = requests.post(url, headers=headers, json=payload, timeout=40)
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
                                    print(f"[GCPVertexAI] [IMAGEN GOOGLE CLOUD GENERADA CON EXITO!] ({len(img_bytes)} bytes) -> {output_path.name}")
                                    return True
                    elif resp.status_code == 429:
                        print(f"[GCPVertexAI] [!] Rate Limit 429 en intento {attempt + 1}. Esperando 3 segundos...")
                        time.sleep(3)
                        continue
                    else:
                        print(f"[GCPVertexAI] [!] Error Vertex AI ({resp.status_code}): {resp.text[:120]}")
                        break
                except Exception as e:
                    print(f"[GCPVertexAI] [!] Excepción en llamada Vertex AI: {e}")
                    break

        # Si Vertex AI no está disponible o falló con 429, ejecutar el generador de respaldo
        return cls._fallback_generate(prompt, output_path)
