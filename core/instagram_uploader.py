import os
import requests
import time
from pathlib import Path
from typing import Dict, Any, Optional

class InstagramUploader:
    """Publicador de Instagram Reels mediante Instagram Graph API v20.0."""

    def __init__(self, ig_account_id: Optional[str] = None, access_token: Optional[str] = None):
        self.ig_account_id = ig_account_id or os.getenv("INSTAGRAM_ACCOUNT_ID", "")
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.api_version = "v20.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def upload_reel_resumable(self, video_path: Path, caption: str) -> Dict[str, Any]:
        """Sube y publica un Reel en Instagram Business/Creator mediante Resumable Upload API."""
        if not self.ig_account_id or not self.access_token:
            print("[InstagramUploader] [!] INSTAGRAM_ACCOUNT_ID o FACEBOOK_ACCESS_TOKEN no configurados. Omitiendo Instagram.")
            return {"success": False, "skipped": True, "reason": "No credentials"}

        file_size = os.path.getsize(video_path)
        print(f"[InstagramUploader] Iniciando subida de Reel a Instagram ({file_size / (1024*1024):.2f} MB)...")

        # Paso 1: Crear contenedor de subida resumable en Instagram
        init_url = f"{self.base_url}/{self.ig_account_id}/media"
        init_payload = {
            "media_type": "REELS",
            "upload_type": "resumable",
            "caption": caption,
            "access_token": self.access_token
        }
        res = requests.post(init_url, data=init_payload, timeout=25)
        res_data = res.json()

        if "id" not in res_data or "uri" not in res_data:
            print(f"[InstagramUploader] [!] Error al iniciar contenedor de Instagram: {res_data}")
            return {"success": False, "error": res_data}

        container_id = res_data["id"]
        upload_uri = res_data["uri"]
        print(f"[InstagramUploader] Contenedor de Instagram creado (ID: {container_id}). Subiendo video...")

        # Paso 2: Subir archivo binario al endpoint uri
        with open(video_path, "rb") as vf:
            headers = {
                "Authorization": f"OAuth {self.access_token}",
                "offset": "0",
                "file_size": str(file_size)
            }
            upload_res = requests.post(upload_uri, headers=headers, data=vf, timeout=180)

        if upload_res.status_code not in [200, 201]:
            print(f"[InstagramUploader] [!] Falló la transferencia a Instagram: {upload_res.text}")
            return {"success": False, "error": upload_res.text}

        print("[InstagramUploader] Video transferido a Instagram. Esperando procesamiento de Meta...")

        # Paso 3: Esperar a que el contenedor termine de procesarse
        status_url = f"{self.base_url}/{container_id}"
        params = {"fields": "status_code", "access_token": self.access_token}
        for _ in range(12):
            time.sleep(5)
            s_res = requests.get(status_url, params=params, timeout=15).json()
            status_code = s_res.get("status_code", "")
            if status_code == "FINISHED":
                print("[InstagramUploader] Contenedor procesado con éxito por Meta.")
                break
            elif status_code == "ERROR":
                return {"success": False, "error": f"Error de procesamiento en Instagram: {s_res}"}

        # Paso 4: Publicar contenedor en Instagram Reels
        pub_url = f"{self.base_url}/{self.ig_account_id}/media_publish"
        pub_payload = {
            "creation_id": container_id,
            "access_token": self.access_token
        }
        pub_res = requests.post(pub_url, data=pub_payload, timeout=25).json()

        if "id" in pub_res:
            print(f"[InstagramUploader] [¡ÉXITO TOTAL! 🚀] Reel publicado en Instagram (ID: {pub_res['id']})")
            return {"success": True, "media_id": pub_res["id"]}
        else:
            print(f"[InstagramUploader] [!] Error al publicar en Instagram: {pub_res}")
            return {"success": False, "error": pub_res}
