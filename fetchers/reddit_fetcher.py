import subprocess
import requests
import re
from pathlib import Path
from typing import Optional, List

REDDIT_HEADERS = {
    "User-Agent": "CuriosityApp/1.0 (educational-video-project; contact@curiosityproject.org)"
}

def search_reddit_videos(keyword: str, max_results: int = 3) -> List[dict]:
    """
    Busca videos relevantes en Reddit en una sola petición global rápida.
    """
    clean_query = re.sub(r'[^\w\s]', '', keyword).strip()
    url = "https://www.reddit.com/search.json"
    params = {
        "q": f"{clean_query} video",
        "sort": "relevance",
        "limit": max_results * 2
    }

    found_videos = []
    try:
        resp = requests.get(url, headers=REDDIT_HEADERS, params=params, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                pdata = post.get("data", {})
                permalink = pdata.get("permalink", "")
                is_video = pdata.get("is_video", False)
                title = pdata.get("title", "")
                
                if is_video or "v.redd.it" in pdata.get("url", ""):
                    found_videos.append({
                        "source": "reddit",
                        "title": title,
                        "url": f"https://www.reddit.com{permalink}"
                    })
                    if len(found_videos) >= max_results:
                        break
    except Exception as e:
        print(f"[RedditFetcher] Error: {e}")

    return found_videos

def download_reddit_video(post_url: str, output_path: Path) -> bool:
    """Descarga video de Reddit de forma rápida con yt-dlp."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--socket-timeout", "6",
        "-f", "best[height<=720]/best",
        "--merge-output-format", "mp4",
        "-o", str(output_path),
        "--force-overwrites",
        post_url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=12)
        return res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 1000
    except Exception:
        return False
