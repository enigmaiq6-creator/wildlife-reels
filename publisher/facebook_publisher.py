import os
import time
import json
import requests
from pathlib import Path
from typing import Optional, Dict, Any

BASE_DIR = Path(__file__).resolve().parent.parent

def load_env_file():
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")

load_env_file()

class FacebookPublisher:
    """
    Publicador Automático Oficial a Facebook Reels (Wild Vault)
    utilizando Facebook Graph API v19.0
    """

    def __init__(self, page_id: Optional[str] = None, access_token: Optional[str] = None):
        load_env_file()
        self.page_id = page_id or os.environ.get("FB_PAGE_ID", "1269051872959609")
        self.access_token = access_token or os.environ.get("FB_PAGE_ACCESS_TOKEN", "")

    def is_configured(self) -> bool:
        return bool(self.page_id and self.access_token)

    def publish_reel(
        self,
        video_path: Path,
        title: str,
        description: str,
        hashtags: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sube y publica un video en formato Reel en la página de Facebook.
        """
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"[FacebookPublisher] [!] Error: El video no existe en {video_path}")
            return None

        if not self.is_configured():
            print("[FacebookPublisher] [!] Error: FB_PAGE_ID o FB_PAGE_ACCESS_TOKEN no configurados en .env")
            return None

        file_size = video_path.stat().st_size
        full_caption = f"{title}\n\n{description}"
        if hashtags:
            full_caption += f"\n\n{hashtags}"

        print(f"\n[FacebookPublisher] [INICIANDO SUBIDA A FACEBOOK REELS]")
        print(f"  -> Pagina: Wild Vault (ID: {self.page_id})")
        print(f"  -> Archivo: {video_path.name} ({file_size / (1024*1024):.2f} MB)")

        # PASO 1: Inicializar sesión de subida de Reel
        init_url = f"https://graph.facebook.com/v19.0/{self.page_id}/video_reels"
        init_payload = {
            "upload_phase": "start",
            "access_token": self.access_token
        }

        try:
            init_res = requests.post(init_url, data=init_payload, timeout=30)
            if init_res.status_code != 200:
                print(f"[FacebookPublisher] [!] Error inicializando sesion: {init_res.text}")
                return None

            init_data = init_res.json()
            video_id = init_data.get("video_id")
            upload_url = init_data.get("upload_url") or f"https://rupload.facebook.com/video-upload/v19.0/{video_id}"
            print(f"[FacebookPublisher] [+] Sesion creada. Video ID: {video_id}")
        except Exception as e:
            print(f"[FacebookPublisher] [!] Excepcion en inicializacion: {e}")
            return None

        # PASO 2: Subir archivo binario
        headers = {
            "Authorization": f"OAuth {self.access_token}",
            "offset": "0",
            "file_size": str(file_size),
            "Content-Type": "application/octet-stream"
        }

        try:
            print(f"[FacebookPublisher] [SUBIENDO VIDEO BINARIO] ({file_size / (1024*1024):.2f} MB)...")
            with open(video_path, "rb") as f:
                video_data = f.read()

            upload_res = requests.post(upload_url, headers=headers, data=video_data, timeout=180)
            if upload_res.status_code not in (200, 201):
                print(f"[FacebookPublisher] [!] Error subiendo video: {upload_res.text}")
                return None

            print(f"[FacebookPublisher] [+] Video binario transferido con exito.")
        except Exception as e:
            print(f"[FacebookPublisher] [!] Excepcion subiendo video: {e}")
            return None

        # PASO 3: Esperar procesamiento de Facebook
        print("[FacebookPublisher] [ESPERANDO PROCESAMIENTO EN SERVIDORES DE META] (7 seg)...")
        time.sleep(7)

        # PASO 4: Publicar el Reel
        finish_url = f"https://graph.facebook.com/v19.0/{self.page_id}/video_reels"
        finish_payload = {
            "upload_phase": "finish",
            "access_token": self.access_token,
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": full_caption
        }

        try:
            finish_res = requests.post(finish_url, data=finish_payload, timeout=30)
            if finish_res.status_code != 200:
                print(f"[FacebookPublisher] [!] Error finalizando publicacion: {finish_res.text}")
                return None

            result = finish_res.json()
            post_id = result.get("post_id") or video_id
            print(f"\n[FacebookPublisher] [¡REEL PUBLICADO CON EXITO EN WILD VAULT!]")
            print(f"  -> Video ID: {video_id}")
            print(f"  -> Post ID: {post_id}")
            print(f"  -> Link: https://www.facebook.com/{self.page_id}/videos/{video_id}")
            return result
        except Exception as e:
            print(f"[FacebookPublisher] [!] Excepcion al publicar Reel: {e}")
            return None

    def publish_photo(
        self,
        image_path: Path,
        caption: str
    ) -> Optional[Dict[str, Any]]:
        """
        Sube y publica una foto en la página de Facebook de Wild Vault.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            print(f"[FacebookPublisher] [!] Error: La imagen no existe en {image_path}")
            return None

        if not self.is_configured():
            print("[FacebookPublisher] [!] Error: FB_PAGE_ID o FB_PAGE_ACCESS_TOKEN no configurados en .env")
            return None

        file_size = image_path.stat().st_size
        print(f"\n[FacebookPublisher] [INICIANDO SUBIDA DE FOTO A WILD VAULT]")
        print(f"  -> Pagina: Wild Vault (ID: {self.page_id})")
        print(f"  -> Archivo: {image_path.name} ({file_size / 1024:.2f} KB)")

        url = f"https://graph.facebook.com/v19.0/{self.page_id}/photos"
        payload = {
            "caption": caption,
            "access_token": self.access_token,
            "published": "true"
        }

        try:
            with open(image_path, "rb") as f:
                files = {"source": (image_path.name, f, "image/jpeg")}
                res = requests.post(url, data=payload, files=files, timeout=60)

            if res.status_code != 200:
                print(f"[FacebookPublisher] [!] Error publicando foto: {res.text}")
                return None

            result = res.json()
            photo_id = result.get("id")
            post_id = result.get("post_id") or photo_id
            print(f"\n[FacebookPublisher] [¡IMAGEN PUBLICADA CON ÉXITO EN WILD VAULT!]")
            print(f"  -> Photo ID: {photo_id}")
            print(f"  -> Post ID: {post_id}")
            print(f"  -> Link: https://www.facebook.com/{self.page_id}/photos/{photo_id}")
            return result
        except Exception as e:
            print(f"[FacebookPublisher] [!] Excepción al publicar foto: {e}")
            return None

