import json
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from datetime import datetime

class HistoryManager:
    """Administrador de historial persistente para garantizar CERO REPETICIÓN de criaturas, clips de video e imágenes."""

    def __init__(self, history_file: Path = Path("history.json")):
        self.history_file = history_file
        if not self.history_file.exists():
            self._init_history()

    def _init_history(self):
        default_data = {
            "published_topics": [],
            "used_video_urls": [],
            "used_image_urls": [],
            "total_published": 0,
            "last_updated": ""
        }
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)

    def load_history(self) -> Dict[str, Any]:
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "used_video_urls" not in data:
                    data["used_video_urls"] = []
                if "used_image_urls" not in data:
                    data["used_image_urls"] = []
                return data
        except Exception:
            self._init_history()
            return {"published_topics": [], "used_video_urls": [], "used_image_urls": [], "total_published": 0}

    def save_history(self, data: Dict[str, Any]):
        """Escribe atómicamente el historial a disco."""
        try:
            temp_file = self.history_file.with_suffix(".tmp")
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            temp_file.replace(self.history_file)
        except Exception as e:
            print(f"[HistoryManager] Error guardando historial: {e}")
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def get_seen_topics(self) -> List[str]:
        data = self.load_history()
        return [entry["topic_id"] for entry in data.get("published_topics", []) if "topic_id" in entry]

    def get_used_video_urls(self) -> Set[str]:
        data = self.load_history()
        return set(data.get("used_video_urls", []))

    def get_used_image_urls(self) -> Set[str]:
        data = self.load_history()
        return set(data.get("used_image_urls", []))

    def record_published_topic(
        self,
        topic_id: str,
        title: str,
        creature_name: str = "",
        post_id: str = "",
        clips_used: Optional[List[str]] = None,
        images_used: Optional[List[str]] = None
    ):
        data = self.load_history()
        
        # Actualizar lista de temas
        new_entry = {
            "topic_id": topic_id,
            "title": title,
            "creature_name": creature_name,
            "published_at": datetime.utcnow().isoformat(),
            "post_id": post_id
        }
        if clips_used:
            new_entry["clips_count"] = len(clips_used)
        if images_used:
            new_entry["images_count"] = len(images_used)

        data["published_topics"].append(new_entry)
        data["total_published"] = len(data["published_topics"])
        data["last_updated"] = datetime.utcnow().isoformat()

        # Actualizar URLs de medios utilizados para evitar reutilización histórica
        current_videos = set(data.get("used_video_urls", []))
        if clips_used:
            for u in clips_used:
                if u and isinstance(u, str):
                    current_videos.add(u)
        data["used_video_urls"] = list(current_videos)

        current_images = set(data.get("used_image_urls", []))
        if images_used:
            for img in images_used:
                if img and isinstance(img, str):
                    current_images.add(img)
        data["used_image_urls"] = list(current_images)

        # Guardar inmediatamente a disco
        self.save_history(data)

        safe_tid = str(topic_id).encode('ascii', 'ignore').decode()
        safe_cn = str(creature_name).encode('ascii', 'ignore').decode()
        print(f"[HistoryManager] [OK] Registrado '{safe_tid}' ({safe_cn}) en history.json con exito (Total: {data['total_published']} | Videos guardados: {len(data['used_video_urls'])}).")

