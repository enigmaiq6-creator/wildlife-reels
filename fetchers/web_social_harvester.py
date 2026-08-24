import urllib.request
import urllib.parse
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Dict
from config import TEMP_DIR

class WebSocialHarvester:
    """
    Cosechador Automático Multi-Clip de Redes Sociales (Facebook, Reddit, TikTok, Web):
    - Busca metraje real del animal en múltiples plataformas abiertas.
    - Descarga el video completo y lo segmenta automáticamente en 6-8 tomas verticales de acción.
    - Garantiza que toda la secuencia del micro-documental use VIDEOS REALES del animal.
    """

    used_urls: set = set()

    @classmethod
    def reset_session(cls):
        cls.used_urls.clear()

    @staticmethod
    def search_social_video_urls(query: str, platforms: Optional[List[str]] = None, max_results: int = 5) -> List[str]:
        """Busca URLs públicas de videos a través de DuckDuckGo en plataformas clave de video."""
        if platforms is None:
            platforms = ["facebook.com", "reddit.com", "tiktok.com"]

        found_links = []
        for platform in platforms:
            full_query = f"site:{platform} {query} video"
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(full_query)}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    html = r.read().decode("utf-8")
                    raw_links = re.findall(r'uddg=([^&]+)', html)
                    for link in raw_links:
                        unquoted = urllib.parse.unquote(link)
                        if platform in unquoted and any(p in unquoted for p in ["video", "reel", "watch", "post", "comments"]):
                            if unquoted not in found_links and unquoted not in WebSocialHarvester.used_urls:
                                found_links.append(unquoted)
                                if len(found_links) >= max_results:
                                    break
            except Exception as e:
                pass

        return found_links

    @classmethod
    def harvest_and_slice_vault(cls, animal_name: str, target_dir: Path, num_shots: int = 8) -> int:
        """
        Descarga videos reales del animal desde redes sociales y los rebana en múltiples
        tomas verticales (1080x1920) de 3.5s listas para cada escena del guion.
        """
        target_dir.mkdir(parents=True, exist_ok=True)
        query_animal = animal_name.lower().replace("-", " ").replace("_", " ").strip()
        search_terms = [
            f"{query_animal} attack hunt wildlife",
            f"{query_animal} close up face eyes",
            f"{query_animal} nature documentary 4k",
            f"{query_animal} predator move wild"
        ]

        raw_video_path = TEMP_DIR / f"{animal_name}_social_raw.mp4"
        extracted_count = 0

        for term in search_terms:
            if extracted_count >= num_shots:
                break

            urls = cls.search_social_video_urls(term, max_results=4)
            for video_url in urls:
                if video_url in cls.used_urls:
                    continue
                cls.used_urls.add(video_url)

                if raw_video_path.exists():
                    try:
                        raw_video_path.unlink()
                    except Exception:
                        pass

                cmd = [
                    "yt-dlp",
                    "--no-playlist",
                    "--socket-timeout", "15",
                    "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best[height<=720]/best",
                    "--merge-output-format", "mp4",
                    "-o", str(raw_video_path),
                    "--force-overwrites",
                    video_url
                ]
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=35)
                    if res.returncode == 0 and raw_video_path.exists() and raw_video_path.stat().st_size > 100000:
                        # Medir duración
                        cmd_dur = [
                            "ffprobe", "-v", "error",
                            "-show_entries", "format=duration",
                            "-of", "default=noprint_wrappers=1:nokey=1",
                            str(raw_video_path)
                        ]
                        r_dur = subprocess.run(cmd_dur, capture_output=True, text=True, timeout=8)
                        total_dur = float(r_dur.stdout.strip())
                        print(f"[WebSocialHarvester] [+] Video documental descargado: {video_url[:65]} ({total_dur:.1f}s)", flush=True)

                        # Extraer cortes de 3.5 segundos a lo largo del video
                        step = max(3.0, (total_dur - 4.0) / max(1, num_shots - extracted_count))
                        shots_to_extract = min(num_shots - extracted_count, max(1, int(total_dur // 3.5)))

                        for i in range(shots_to_extract):
                            start_t = 0.5 + (i * step)
                            if start_t + 3.0 > total_dur:
                                break
                            clip_idx = extracted_count + 1
                            out_file = target_dir / f"social_clip_{clip_idx:02d}.mp4"

                            cmd_cut = [
                                "ffmpeg", "-y",
                                "-ss", f"{start_t:.2f}",
                                "-i", str(raw_video_path),
                                "-t", "3.5",
                                "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                                "-c:v", "libx264",
                                "-preset", "veryfast",
                                "-crf", "20",
                                "-an",
                                str(out_file)
                            ]
                            subprocess.run(cmd_cut, capture_output=True)
                            if out_file.exists() and out_file.stat().st_size > 25000:
                                extracted_count += 1

                        try:
                            raw_video_path.unlink()
                        except Exception:
                            pass

                        if extracted_count >= 5:
                            print(f"[WebSocialHarvester] [¡ÉXITO TOTAL! 🎬] {extracted_count} clips de video reales extraídos para '{animal_name}'", flush=True)
                            return extracted_count

                except Exception as e:
                    continue

        return extracted_count

    @classmethod
    def harvest_best_clip(cls, animal_name: str, specific_action: str, output_path: Path, target_duration: float = 6.0) -> bool:
        """Descarga directa de un clip individual si se solicita específicamente."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        search_terms = [
            f"{animal_name} {specific_action}",
            f"{animal_name} wildlife 4k"
        ]

        for term in search_terms:
            urls = cls.search_social_video_urls(term, max_results=3)
            for video_url in urls:
                if video_url in cls.used_urls:
                    continue
                cls.used_urls.add(video_url)
                cmd = [
                    "yt-dlp",
                    "--no-playlist",
                    "--socket-timeout", "15",
                    "-f", "bestvideo[height<=1080]+bestaudio/best[height<=1080]/best",
                    "--merge-output-format", "mp4",
                    "-o", str(output_path),
                    "--force-overwrites",
                    video_url
                ]
                try:
                    res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                    if res.returncode == 0 and output_path.exists() and output_path.stat().st_size > 50000:
                        return True
                except Exception:
                    continue
        return False
