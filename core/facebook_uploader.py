import os
import requests
from pathlib import Path
from typing import Dict, Any, Optional

class FacebookUploader:
    """Publicador de Reels en Páginas de Facebook mediante Meta Graph API v20.0."""

    def __init__(self, page_id: Optional[str] = None, access_token: Optional[str] = None):
        self.page_id = page_id or os.getenv("FACEBOOK_PAGE_ID", "")
        self.access_token = access_token or os.getenv("FACEBOOK_ACCESS_TOKEN", "")
        self.api_version = "v20.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def upload_reel(self, video_path: Path, description: str) -> Dict[str, Any]:
        """Sube y publica un Reel en la Página de Facebook."""
        if not self.page_id or not self.access_token:
            return {"success": False, "error": "Credenciales FACEBOOK_PAGE_ID o FACEBOOK_ACCESS_TOKEN no configuradas"}

        file_size = os.path.getsize(video_path)
        print(f"[FacebookUploader] Iniciando subida de Reel ({file_size / (1024*1024):.2f} MB)...")

        # Paso 1: Iniciar sesión de subida de Reel
        init_url = f"{self.base_url}/{self.page_id}/video_reels"
        init_payload = {
            "upload_phase": "start",
            "access_token": self.access_token
        }
        res = requests.post(init_url, data=init_payload, timeout=20)
        res_data = res.json()

        if "video_id" not in res_data:
            return {"success": False, "error": f"Fallo al iniciar sesión: {res_data}"}

        video_id = res_data["video_id"]
        upload_url = res_data["upload_url"]
        print(f"[FacebookUploader] Sesión iniciada con éxito. Video ID: {video_id}")

        # Paso 2: Transferir archivo binario
        print("[FacebookUploader] Transfiriendo archivo binario de video a los servidores de Meta...")
        with open(video_path, "rb") as video_file:
            headers = {
                "Authorization": f"OAuth {self.access_token}",
                "offset": "0",
                "file_size": str(file_size)
            }
            upload_res = requests.post(upload_url, headers=headers, data=video_file, timeout=180)

        if upload_res.status_code not in [200, 201]:
            return {"success": False, "error": f"Fallo en la transferencia binaria: {upload_res.text}"}

        print("[FacebookUploader] Transferencia de video completada al 100%.")

        # Paso 3: Publicar Reel con descripción y hashtags
        print("[FacebookUploader] Publicando Reel con descripción y hashtags...")
        publish_payload = {
            "upload_phase": "finish",
            "access_token": self.access_token,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": description
        }
        pub_res = requests.post(init_url, data=publish_payload, timeout=20)
        pub_data = pub_res.json()

        if pub_data.get("success") is True or "post_id" in pub_data:
            print(f"[FacebookUploader] [¡ÉXITO TOTAL! 🚀] Reel publicado en Facebook: {pub_data}")
            return {"success": True, "video_id": video_id, "data": pub_data}
        else:
            return {"success": False, "error": f"Error al finalizar publicación: {pub_data}"}
