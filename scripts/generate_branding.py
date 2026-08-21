import base64
import requests
from pathlib import Path
from google.oauth2 import service_account
import google.auth.transport.requests

BASE_DIR = Path(__file__).resolve().parent.parent
CREDENTIALS_PATH = BASE_DIR / "credentials" / "gcp_service_account.json"
OUT_DIR = BASE_DIR / "output" / "branding"
OUT_DIR.mkdir(parents=True, exist_ok=True)

creds = service_account.Credentials.from_service_account_file(
    str(CREDENTIALS_PATH),
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)
creds.refresh(google.auth.transport.requests.Request())
token = creds.token

items = [
    {
        "name": "facebook_profile_pic.jpg",
        "prompt": "Award-winning National Geographic portrait, centered close-up of a fierce black jaguar face emerging from dark shadowy background, glowing amber-gold eyes looking directly at camera, razor sharp focus, volumetric dark cinematic lighting, 8k resolution, photorealistic luxury branding avatar",
        "aspect_ratio": "1:1"
    },
    {
        "name": "facebook_cover_banner.jpg",
        "prompt": "Epic widescreen panoramic landscape of an untamed misty rainforest wilderness at sunrise, a massive apex Harpy Eagle perched on a giant branch overlooking a vast jungle canyon with dramatic golden hour god rays piercing through misty trees, 8k resolution, ultra photorealistic BBC Earth documentary style",
        "aspect_ratio": "16:9"
    }
]

url = "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/facebookbot-502117/locations/us-central1/publishers/google/models/gemini-2.5-flash-image:generateContent"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json; charset=utf-8"
}

for item in items:
    name = item["name"]
    prompt = item["prompt"]
    print(f"[Branding] Generando {name} con Google Cloud Vertex AI...")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]}
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if resp.status_code == 200:
        candidates = resp.json().get("candidates", [])
        if candidates:
            parts = candidates[0].get("content", {}).get("parts", [])
            for p in parts:
                if "inlineData" in p:
                    b64 = p["inlineData"]["data"]
                    target = OUT_DIR / name
                    target.write_bytes(base64.b64decode(b64))
                    print(f"[Branding] [OK] {name} guardado con exito en {target} ({target.stat().st_size} bytes)")
    else:
        print(f"[Branding] [ERR] {name}: {resp.status_code} - {resp.text[:120]}")
