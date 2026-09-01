import sys
import json
from pathlib import Path

def merge_histories(runner_history_path="/tmp/run_history.json", repo_history_path="history.json"):
    runner_p = Path(runner_history_path)
    repo_p = Path(repo_history_path)

    if not runner_p.exists():
        print(f"[MergeHistory] No runner history found at {runner_p}. Skipping.")
        return

    try:
        with open(runner_p, "r", encoding="utf-8") as f:
            local_data = json.load(f)
    except Exception as e:
        print(f"[MergeHistory] Error reading {runner_p}: {e}")
        return

    try:
        if repo_p.exists():
            with open(repo_p, "r", encoding="utf-8") as f:
                remote_data = json.load(f)
        else:
            remote_data = {"published_topics": [], "used_video_urls": [], "used_image_urls": []}
    except Exception:
        remote_data = {"published_topics": [], "used_video_urls": [], "used_image_urls": []}

    seen = set()
    merged_topics = []
    for t in remote_data.get("published_topics", []) + local_data.get("published_topics", []):
        key = (t.get("topic_id", ""), t.get("published_at", ""))
        if key not in seen:
            seen.add(key)
            merged_topics.append(t)

    remote_data["published_topics"] = merged_topics
    remote_data["total_published"] = len(merged_topics)
    remote_data["used_video_urls"] = list(set(remote_data.get("used_video_urls", []) + local_data.get("used_video_urls", [])))
    remote_data["used_image_urls"] = list(set(remote_data.get("used_image_urls", []) + local_data.get("used_image_urls", [])))
    remote_data["last_updated"] = local_data.get("last_updated", "")

    with open(repo_p, "w", encoding="utf-8") as f:
        json.dump(remote_data, f, indent=2, ensure_ascii=False)

    print(f"[MergeHistory] [SUCCESS] Merged history.json successfully. Total topics: {len(merged_topics)} | Video URLs: {len(remote_data['used_video_urls'])}")

if __name__ == "__main__":
    r_path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/run_history.json"
    dest_path = sys.argv[2] if len(sys.argv) > 2 else "history.json"
    merge_histories(r_path, dest_path)
