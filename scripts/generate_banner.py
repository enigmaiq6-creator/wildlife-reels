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

url = "https://us-central1-aiplatform.googleapis.com/v1beta1/projects/facebookbot-502117/locations/us-central1/publishers/google/models/gemini-2.5-flash-image:generateContent"
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json; charset=utf-8"
}

banner_path = OUT_DIR / "facebook_cover_banner.jpg"
prompt = (
    "National Geographic widescreen panoramic 8k photography for a Facebook cover banner. "
    "A vast primordial jungle river landscape at sunrise with an intense apex black jaguar and harpy eagle in the distance, "
    "golden hour god rays piercing through misty rainforest canopy, razor sharp focus, volumetric lighting, luxury documentary aesthetic."
)

print("[Branding] Generando facebook_cover_banner.jpg con Google Cloud Vertex AI...")
payload = {
    "contents": [{"role": "user", "parts": [{"text": prompt}]}],
    "generationConfig": {"responseModalities": ["IMAGE"]}
}

resp = requests.post(url, headers=headers, json=payload, timeout=120)
if resp.status_code == 200:
    candidates = resp.json().get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        for p in parts:
            if "inlineData" in p:
                b64 = p["inlineData"]["data"]
                banner_path.write_bytes(base64.b64decode(b64))
                print(f"[Branding] [OK] facebook_cover_banner.jpg guardado en {banner_path} ({banner_path.stat().st_size} bytes)")
else:
    print(f"[Branding] [ERR] Status {resp.status_code}: {resp.text[:150]}")
