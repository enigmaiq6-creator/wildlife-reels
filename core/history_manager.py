import json
from pathlib import Path
from typing import List, Dict, Any

class HistoryManager:
    """Administrador de historial persistente para garantizar CERO REPETICIÓN de temas de Vida Salvaje."""

    def __init__(self, history_file: Path = Path("history.json")):
        self.history_file = history_file
        if not self.history_file.exists():
            self._init_history()

    def _init_history(self):
        default_data = {
            "published_topics": [],
            "total_published": 0,
            "last_updated": ""
        }
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)

    def load_history(self) -> Dict[str, Any]:
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            self._init_history()
            return {"published_topics": [], "total_published": 0}

    def get_seen_topics(self) -> List[str]:
        data = self.load_history()
        return [entry["topic_id"] for entry in data.get("published_topics", []) if "topic_id" in entry]

    def record_published_topic(self, topic_id: str, title: str, creature_name: str = "", post_id: str = ""):
        from datetime import datetime
        data = self.load_history()
        data["published_topics"].append({
            "topic_id": topic_id,
            "title": title,
            "creature_name": creature_name,
            "published_at": datetime.utcnow().isoformat(),
            "post_id": post_id
        })
        data["total_published"] = len(data["published_topics"])
        data["last_updated"] = datetime.utcnow().isoformat()

        safe_tid = str(topic_id).encode('ascii', 'ignore').decode()
        safe_cn = str(creature_name).encode('ascii', 'ignore').decode()
        print(f"[HistoryManager] [OK] Registrado '{safe_tid}' ({safe_cn}) en history.json con exito.")
