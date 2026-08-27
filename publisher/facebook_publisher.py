import os
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class FacebookPublisher:
    """
    Publicador Oficial de Contenido en Facebook (Meta Graph API v19.0) para Wild Vault:
    - Sube y publica Reels (Videos 9:16) con descripción y hashtags en inglés.
    - Sube y publica Imágenes multi-formato (1080x1350) con descripciones completas.
    - Incluye etiqueta de transparencia y descargo de responsabilidad de IA (AI Transparency).
    - Publica automáticamente el primer comentario interactivo (Auto-Comment Poll / Question) en inglés.
    """

    def __init__(self):
        self.page_id = (
            os.getenv("FACEBOOK_PAGE_ID") or 
            os.getenv("FB_PAGE_ID", "122180816492897912")
        )
        self.access_token = (
            os.getenv("FACEBOOK_ACCESS_TOKEN") or 
            os.getenv("FB_PAGE_ACCESS_TOKEN", "")
        )

    def is_configured(self) -> bool:
        """Verifica si las credenciales están presentes."""
        return bool(self.page_id and self.access_token)

    def post_comment(self, object_id: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Publica un comentario de alto engagement en el Reel o Foto de Facebook.
        """
        if not self.is_configured() or not object_id or not message:
            return None

        url = f"https://graph.facebook.com/v19.0/{object_id}/comments"
        payload = {
            "message": message,
            "access_token": self.access_token
        }

        try:
            print(f"[FacebookPublisher] [+] Publicando auto-comentario de interacción en objeto '{object_id}'...")
            res = requests.post(url, data=payload, timeout=20)
            if res.status_code == 200:
                result = res.json()
                print(f"[FacebookPublisher] [✓] Auto-comentario publicado con éxito en Facebook (ID: {result.get('id')})")
                return result
            else:
                print(f"[FacebookPublisher] [!] Nota: Comentario no publicado ({res.status_code}): {res.text}")
        except Exception as e:
            print(f"[FacebookPublisher] [!] Excepción publicando comentario: {e}")
        return None

    def publish_reel(
        self,
        video_path: Path,
        title: str,
        description: str,
        hashtags: str = "",
        comment_text: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Sube y publica un video en Facebook Reels con Meta Graph API en 4 pasos.
        Incluye descargo de IA y auto-comentario.
        """
        video_path = Path(video_path)
        if not video_path.exists():
            print(f"[FacebookPublisher] [!] Error: El archivo de video no existe en {video_path}")
            return None

        if not self.is_configured():
            print("[FacebookPublisher] [!] Error: FB_PAGE_ID o FB_PAGE_ACCESS_TOKEN no configurados en .env")
            return None

        file_size = video_path.stat().st_size
        
        # Etiqueta obligatoria y profesional de transparencia de IA en inglés
        ai_transparency_footer = (
            "\n\n---\n"
            "🤖 AI Transparency: Content produced with AI assistance for wildlife education & entertainment.\n"
            "✨ Produced by Wild Vault"
        )

        full_caption = f"{title}\n\n{description}"
        if hashtags:
            full_caption += f"\n\n{hashtags}"
        full_caption += ai_transparency_footer

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

            # PASO 5: Auto-Comentario interactivo
            if comment_text:
                time.sleep(4)
                # Intentar publicar en el post_id y video_id
                self.post_comment(post_id, comment_text)

            return result
        except Exception as e:
            print(f"[FacebookPublisher] [!] Excepcion al publicar Reel: {e}")
            return None

    def publish_photo(
        self,
        image_path: Path,
        caption: str,
        comment_text: Optional[str] = None
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

        ai_transparency_footer = (
            "\n\n---\n"
            "🤖 AI Transparency: Content produced with AI assistance for wildlife education & entertainment.\n"
            "✨ Produced by Wild Vault"
        )
        full_caption = caption + ai_transparency_footer

        print(f"\n[FacebookPublisher] [PUBLICANDO FOTO EN FACEBOOK]")
        print(f"  -> Pagina: Wild Vault (ID: {self.page_id})")
        print(f"  -> Imagen: {image_path.name}")

        url = f"https://graph.facebook.com/v19.0/{self.page_id}/photos"
        payload = {
            "caption": full_caption,
            "access_token": self.access_token
        }

        try:
            with open(image_path, "rb") as img_f:
                files = {"source": img_f}
                res = requests.post(url, data=payload, files=files, timeout=60)

            if res.status_code == 200:
                data = res.json()
                post_id = data.get("post_id") or data.get("id")
                print(f"[FacebookPublisher] [¡FOTO PUBLICADA CON EXITO!] ID: {data.get('id')}")
                
                if comment_text and post_id:
                    time.sleep(3)
                    self.post_comment(post_id, comment_text)

                return data
            else:
                print(f"[FacebookPublisher] [!] Error publicando foto: {res.text}")
                return None
        except Exception as e:
            print(f"[FacebookPublisher] [!] Excepcion al publicar foto: {e}")
            return None
