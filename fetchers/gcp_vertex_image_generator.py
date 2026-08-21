import os
import json
import base64
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
    def generate_image(
        cls,
        prompt: str,
        output_path: Path,
        aspect_ratio: str = "9:16"
    ) -> bool:
        """
        Genera una fotografía fotorrealista de alta definición usando Google Cloud Vertex AI.
        """
        token = cls._get_auth_token()
        if not token:
            return False

        output_path.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://{cls._location}-aiplatform.googleapis.com/v1beta1/projects/{cls._project_id}/locations/{cls._location}/publishers/google/models/gemini-2.5-flash-image:generateContent"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        cinematic_prompt = (
            f"National Geographic photorealistic vertical 4k wildlife photography of {prompt}. "
            f"Award winning wildlife documentary photo, 8k resolution, volumetric natural lighting, razor sharp focus."
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
            else:
                print(f"[GCPVertexAI] [!] Error Vertex AI ({resp.status_code}): {resp.text[:120]}")
        except Exception as e:
            print(f"[GCPVertexAI] [!] Excepcion en llamada a Vertex AI: {e}")

        return False
