import os
import sys
from pathlib import Path
from PIL import ImageFont

class FontManager:
    """
    Gestor Universal de Fuentes Tipográficas de Alta Definición (Windows & Linux / GitHub Actions).
    """

    @classmethod
    def get_font(cls, font_type: str = "bold", size: int = 40):
        """
        Retorna una fuente TrueType según el tipo ('black', 'bold', 'regular', 'serif', 'comic').
        """
        font_candidates = {
            "black": [
                "C:/Windows/Fonts/ariblk.ttf",
                "C:/Windows/Fonts/impact.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
            ],
            "bold": [
                "C:/Windows/Fonts/arialbd.ttf",
                "C:/Windows/Fonts/trebucbd.ttf",
                "C:/Windows/Fonts/segoeuib.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            ],
            "regular": [
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/segoeui.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
            ],
            "italic": [
                "C:/Windows/Fonts/ariali.ttf",
                "C:/Windows/Fonts/georgiai.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf"
            ],
            "serif": [
                "C:/Windows/Fonts/timesbd.ttf",
                "C:/Windows/Fonts/georgiab.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
            ],
            "comic": [
                "C:/Windows/Fonts/comicbd.ttf",
                "C:/Windows/Fonts/comic.ttf",
                "C:/Windows/Fonts/arialbd.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            ]
        }

        paths = font_candidates.get(font_type, font_candidates["bold"])
        for p in paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    continue

        try:
            return ImageFont.load_default()
        except Exception:
            return None
