import urllib.request
import json
import re
from pathlib import Path
from typing import List, Dict, Optional

SUBREDDITS = ["natureismetal", "NatureIsFuckingLit", "wildlife", "AnimalsBeingDerps", "AnimalVideos"]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 WildlifeApp/2.0"
}

def search_reddit_animal_videos(animal_query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Busca videos auténticos de animales salvajes en los subreddits más virales del mundo.
    Extrae enlaces directos a videos MP4 HD de Reddit sin intermediarios.
    """
    clean_query = urllib.parse.quote(animal_query)
    found_videos = []
    
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/search.json?q={clean_query}&restrict_sr=1&sort=relevance&limit=10"
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=6) as response:
                data = json.loads(response.read().decode("utf-8"))
                posts = data.get("data", {}).get("children", [])
                for post in posts:
                    pdata = post.get("data", {})
                    title = pdata.get("title", "")
                    permalink = pdata.get("permalink", "")
                    
                    # 1. Comprobar si tiene video nativo de Reddit (v.redd.it)
                    media = pdata.get("media") or pdata.get("secure_media") or {}
                    reddit_video = media.get("reddit_video") if isinstance(media, dict) else None
                    
                    if reddit_video and "fallback_url" in reddit_video:
                        video_url = reddit_video["fallback_url"]
                        found_videos.append({
                            "source": f"reddit_r/{sub}",
                            "title": title,
                            "direct_video_url": video_url,
                            "post_url": f"https://www.reddit.com{permalink}"
                        })
                    elif pdata.get("is_video"):
                        found_videos.append({
                            "source": f"reddit_r/{sub}",
                            "title": title,
                            "direct_video_url": "",
                            "post_url": f"https://www.reddit.com{permalink}"
                        })
                        
                    if len(found_videos) >= max_results:
                        return found_videos
        except Exception as e:
            continue

    return found_videos
