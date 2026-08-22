import math
import random
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter, ImageOps
from graphics.font_manager import FontManager

class ImageEngine:
    """
    Motor Gráfico Multi-Formato Oficial para Wild Vault (PIL / Pillow):
    Renderiza los 8 formatos visuales virales con tipografía nítida, badges, gradientes y trazados.
    """

    WIDTH = 1080
    HEIGHT = 1350 # Formato 4:5 ideal para Facebook e Instagram Feed

    @staticmethod
    def _create_dark_gradient(width: int, height: int, start_y: int, max_alpha: int = 230) -> Image.Image:
        """Crea una capa de degradado negro transparente para mejorar la legibilidad del texto."""
        gradient = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        for y in range(start_y, height):
            progress = (y - start_y) / (height - start_y)
            alpha = int(max_alpha * (progress ** 1.3))
            draw.line([(0, y), (width, y)], fill=(0, 0, 0, alpha))
        return gradient

    @staticmethod
    def _draw_speech_bubble(draw: ImageDraw.Draw, box: Tuple[int, int, int, int], text: str, font, font_color=(20, 20, 20)):
        """Dibuja un globo de diálogo estilo cómic."""
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([x1, y1, x2, y2], radius=24, fill=(255, 255, 255, 245), outline=(30, 30, 30), width=3)
        # Triángulo del globo
        mid_x = (x1 + x2) // 2
        tail = [(mid_x - 10, y2), (mid_x - 25, y2 + 25), (mid_x + 10, y2)]
        draw.polygon(tail, fill=(255, 255, 255, 245), outline=(30, 30, 30))
        draw.line([(mid_x - 10, y2), (mid_x + 10, y2)], fill=(255, 255, 255, 245), width=4)

        # Centrar texto en el globo
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x1 + (x2 - x1 - tw) // 2
        ty = y1 + (y2 - y1 - th) // 2 - 2
        draw.text((tx, ty), text, font=font, fill=font_color)

    # =========================================================================
    # FORMATO 1: Catálogo Taxonómico Studio (Fondo Negro - 6 a 8 Especies)
    # =========================================================================
    @classmethod
    def render_format_1_taxonomic_catalog(
        cls,
        title: str,
        species_list: List[Dict[str, Any]], # [{"name": "...", "scientific": "...", "image_path": Path}]
        output_path: Path
    ) -> Path:
        canvas = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), (15, 16, 18))
        draw = ImageDraw.Draw(canvas)

        # Título superior
        font_title = FontManager.get_font("black", 58)
        font_name = FontManager.get_font("bold", 24)
        font_sci = FontManager.get_font("italic", 20)

        # Encabezado
        title_bbox = draw.textbbox((0, 0), title.upper(), font=font_title)
        tw = title_bbox[2] - title_bbox[0]
        draw.text(((cls.WIDTH - tw) // 2, 45), title.upper(), font=font_title, fill=(255, 215, 0)) # Amarillo / Oro

        # Brand Badge
        draw.rounded_rectangle([(cls.WIDTH // 2 - 80, 115), (cls.WIDTH // 2 + 80, 142)], radius=10, fill=(30, 35, 45), outline=(255, 215, 0), width=1)
        font_brand = FontManager.get_font("bold", 15)
        draw.text((cls.WIDTH // 2 - 58, 120), "WILD VAULT", font=font_brand, fill=(255, 255, 255))

        # Cuadrícula de especies (2 columnas x 4 filas)
        cols = 2
        rows = 4
        start_y = 160
        cell_w = cls.WIDTH // cols
        cell_h = (cls.HEIGHT - start_y - 20) // rows

        for idx, sp in enumerate(species_list[:8]):
            r = idx // cols
            c = idx % cols
            cx = c * cell_w + cell_w // 2
            top_y = start_y + r * cell_h

            img_p = Path(sp.get("image_path", ""))
            if img_p.exists():
                try:
                    with Image.open(img_p) as sp_img:
                        sp_img = sp_img.convert("RGBA")
                        sp_img = ImageOps.fit(sp_img, (380, 190), method=Image.Resampling.LANCZOS)
                        canvas.paste(sp_img, (cx - 190, top_y), sp_img)
                except Exception:
                    pass

            # Texto de la especie
            num_str = f"{idx + 1}. {sp.get('name', '').upper()}"
            sci_str = f"({sp.get('scientific', '')})"
            
            draw.text((cx, top_y + 200), num_str, font=font_name, fill=(255, 255, 255), anchor="mm")
            draw.text((cx, top_y + 230), sci_str, font=font_sci, fill=(255, 215, 0), anchor="mm")

        canvas.save(output_path, quality=95)
        return output_path

    # =========================================================================
    # FORMATO 2: Split Real vs Ilustración / Animé con Globo de Diálogo
    # =========================================================================
    @classmethod
    def render_format_2_real_vs_illustrated(
        cls,
        top_image_path: Path,
        bottom_image_path: Path,
        dialogue_text: str,
        output_path: Path
    ) -> Path:
        canvas = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), (20, 20, 20))
        half_h = cls.HEIGHT // 2

        # 1. Imagen Superior (Real)
        if Path(top_image_path).exists():
            with Image.open(top_image_path) as top_img:
                top_img = ImageOps.fit(top_img.convert("RGB"), (cls.WIDTH, half_h), method=Image.Resampling.LANCZOS)
                canvas.paste(top_img, (0, 0))

        # 2. Imagen Inferior (Ilustración / Animé)
        if Path(bottom_image_path).exists():
            with Image.open(bottom_image_path) as bot_img:
                bot_img = ImageOps.fit(bot_img.convert("RGB"), (cls.WIDTH, half_h), method=Image.Resampling.LANCZOS)
                canvas.paste(bot_img, (0, half_h))

        draw = ImageDraw.Draw(canvas)

        # Línea divisoria verde neón / blanca de impacto
        draw.line([(0, half_h), (cls.WIDTH, half_h)], fill=(0, 255, 128), width=5)

        # Badge "WILD VAULT" esquina superior
        draw.rounded_rectangle([(30, 30), (190, 75)], radius=12, fill=(0, 0, 0, 180), outline=(0, 255, 128), width=2)
        font_brand = FontManager.get_font("black", 22)
        draw.text((45, 40), "WILD VAULT", font=font_brand, fill=(255, 255, 255))

        # Globo de diálogo en la mitad inferior
        font_comic = FontManager.get_font("comic", 32)
        bubble_box = (cls.WIDTH - 420, half_h + 50, cls.WIDTH - 60, half_h + 170)
        cls._draw_speech_bubble(draw, bubble_box, dialogue_text, font_comic)

        canvas.save(output_path, quality=95)
        return output_path

    # =========================================================================
    # FORMATO 3: Tarjeta de Curiosidad con Círculo de Detalle (PiP Zoom)
    # =========================================================================
    @classmethod
    def render_format_3_curiosity_pip(
        cls,
        main_image_path: Path,
        pip_image_path: Path,
        headline_lines: List[str], # [Texto blanco, Texto amarillo, Texto blanco]
        output_path: Path,
        badge_text: str = "WILD VAULT CURIOSITY"
    ) -> Path:
        canvas = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), (0, 0, 0))

        # 1. Imagen de fondo completa
        if Path(main_image_path).exists():
            with Image.open(main_image_path) as main_img:
                main_img = ImageOps.fit(main_img.convert("RGB"), (cls.WIDTH, cls.HEIGHT), method=Image.Resampling.LANCZOS)
                canvas.paste(main_img, (0, 0))

        # 2. Círculo PiP insertado
        if Path(pip_image_path).exists():
            with Image.open(pip_image_path) as pip_img:
                pip_size = 380
                pip_crop = ImageOps.fit(pip_img.convert("RGBA"), (pip_size, pip_size), method=Image.Resampling.LANCZOS)
                
                # Crear máscara circular
                mask = Image.new("L", (pip_size, pip_size), 0)
                mask_draw = ImageDraw.Draw(mask)
                mask_draw.ellipse((0, 0, pip_size, pip_size), fill=255)
                
                # Pegar círculo
                pip_x, pip_y = 60, 520
                canvas.paste(pip_crop, (pip_x, pip_y), mask)
                
                # Anillo dorado exterior
                draw_ring = ImageDraw.Draw(canvas)
                draw_ring.ellipse((pip_x, pip_y, pip_x + pip_size, pip_y + pip_size), outline=(255, 215, 0), width=8)

        # 3. Degradado oscuro inferior para texto
        gradient = cls._create_dark_gradient(cls.WIDTH, cls.HEIGHT, start_y=750, max_alpha=240)
        canvas.paste(gradient, (0, 0), gradient)

        draw = ImageDraw.Draw(canvas)

        # Badge pill superior al texto
        pill_w, pill_h = 320, 48
        pill_x = (cls.WIDTH - pill_w) // 2
        pill_y = 860
        draw.rounded_rectangle([(pill_x, pill_y), (pill_x + pill_w, pill_y + pill_h)], radius=24, fill=(40, 100, 240), outline=(255, 255, 255), width=2)
        font_pill = FontManager.get_font("black", 20)
        draw.text((cls.WIDTH // 2, pill_y + pill_h // 2), badge_text.upper(), font=font_pill, fill=(255, 255, 255), anchor="mm")

        # Texto titular en 3 líneas de impacto
        font_head = FontManager.get_font("black", 48)
        y_cursor = 950
        colors = [(255, 255, 255), (255, 215, 0), (255, 255, 255), (0, 230, 255)]

        for idx, line in enumerate(headline_lines):
            c = colors[idx % len(colors)]
            draw.text((cls.WIDTH // 2, y_cursor), line.upper(), font=font_head, fill=c, anchor="mm")
            y_cursor += 65

        canvas.save(output_path, quality=95)
        return output_path

    # =========================================================================
    # FORMATO 5: Ficha de Criatura Legendaria / Fósil Viviente (Titular Gigante)
    # =========================================================================
    @classmethod
    def render_format_5_creature_profile(
        cls,
        image_path: Path,
        creature_title: str, # Ej: "EL NAUTILO"
        fact_paragraphs: List[Dict[str, Any]], # [{"text": "Es un fósil viviente...", "highlight": "500 millones de años"}]
        output_path: Path
    ) -> Path:
        canvas = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), (0, 0, 0))

        if Path(image_path).exists():
            with Image.open(image_path) as img:
                img = ImageOps.fit(img.convert("RGB"), (cls.WIDTH, cls.HEIGHT), method=Image.Resampling.LANCZOS)
                canvas.paste(img, (0, 0))

        # Degradado inferior
        gradient = cls._create_dark_gradient(cls.WIDTH, cls.HEIGHT, start_y=600, max_alpha=245)
        canvas.paste(gradient, (0, 0), gradient)

        draw = ImageDraw.Draw(canvas)

        # Titular gigante en Amarillo / Oro
        font_big = FontManager.get_font("black", 100)
        draw.text((60, 680), creature_title.upper(), font=font_big, fill=(255, 220, 0))

        # Párrafos explicativos
        font_body = FontManager.get_font("bold", 40)
        y_cursor = 820

        for item in fact_paragraphs:
            raw_text = item.get("text", "")
            draw.text((60, y_cursor), raw_text, font=font_body, fill=(255, 255, 255))
            y_cursor += 55

        # Brand Footer
        font_sub = FontManager.get_font("black", 22)
        draw.text((cls.WIDTH - 200, cls.HEIGHT - 50), "WILD VAULT", font=font_sub, fill=(255, 220, 0))

        canvas.save(output_path, quality=95)
        return output_path

    # =========================================================================
    # FORMATO 6: Guía de Campo Vintage Pergamino (3x3 - 9 Especies)
    # =========================================================================
    @classmethod
    def render_format_6_vintage_guide(
        cls,
        title: str,
        nine_species: List[Dict[str, Any]], # [{"name": "...", "sci": "...", "desc": "...", "image_path": ...}]
        output_path: Path
    ) -> Path:
        # Fondo Pergamino Cálido
        canvas = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), (242, 234, 216))
        draw = ImageDraw.Draw(canvas)

        font_title = FontManager.get_font("serif", 46)
        draw.text((cls.WIDTH // 2, 50), title.upper(), font=font_title, fill=(35, 25, 20), anchor="mm")

        # Separador ornamental
        draw.line([(250, 85), (cls.WIDTH - 250, 85)], fill=(120, 90, 60), width=2)
        draw.ellipse((cls.WIDTH // 2 - 6, 79, cls.WIDTH // 2 + 6, 91), fill=(120, 90, 60))

        # Cuadrícula 3x3
        cols = 3
        rows = 3
        start_y = 110
        cell_w = cls.WIDTH // cols
        cell_h = (cls.HEIGHT - start_y - 20) // rows

        font_num = FontManager.get_font("black", 18)
        font_name = FontManager.get_font("bold", 22)
        font_sci = FontManager.get_font("italic", 16)
        font_desc = FontManager.get_font("regular", 16)

        for idx, sp in enumerate(nine_species[:9]):
            r = idx // cols
            c = idx % cols
            cx = c * cell_w + cell_w // 2
            cy = start_y + r * cell_h

            img_p = Path(sp.get("image_path", ""))
            if img_p.exists():
                try:
                    with Image.open(img_p) as sp_img:
                        sp_img = ImageOps.fit(sp_img.convert("RGB"), (260, 180), method=Image.Resampling.LANCZOS)
                        canvas.paste(sp_img, (cx - 130, cy + 10))
                except Exception:
                    pass

            # Badge numerado
            badge_y = cy + 210
            draw.ellipse((cx - 110, badge_y - 12, cx - 86, badge_y + 12), fill=(40, 30, 25))
            draw.text((cx - 98, badge_y), str(idx + 1), font=font_num, fill=(255, 255, 255), anchor="mm")

            # Nombre
            draw.text((cx - 75, badge_y), sp.get("name", ""), font=font_name, fill=(20, 15, 10), anchor="lm")
            # Científico
            draw.text((cx, badge_y + 24), f"({sp.get('sci', '')})", font=font_sci, fill=(100, 70, 50), anchor="mm")
            # Descripción
            draw.text((cx, badge_y + 50), sp.get("desc", "")[:45], font=font_desc, fill=(60, 50, 45), anchor="mm")

        canvas.save(output_path, quality=95)
        return output_path

    # =========================================================================
    # FORMATO 7: Noticia Científica / Descubrimiento Prehistórico (Muy Interesante Style)
    # =========================================================================
    @classmethod
    def render_format_7_breaking_news(
        cls,
        image_path: Path,
        headline_text: str, # Ej: "Descubren que un cocodrilo gigante de 7 metros cazaba mamíferos..."
        output_path: Path
    ) -> Path:
        canvas = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), (0, 0, 0))

        if Path(image_path).exists():
            with Image.open(image_path) as img:
                img = ImageOps.fit(img.convert("RGB"), (cls.WIDTH, cls.HEIGHT), method=Image.Resampling.LANCZOS)
                canvas.paste(img, (0, 0))

        # 1. Badge Superior Rojo "WILD VAULT / SCIENCE DISCOVERY"
        draw = ImageDraw.Draw(canvas)
        draw.rectangle([(cls.WIDTH // 2 - 130, 40), (cls.WIDTH // 2 + 130, 95)], fill=(220, 20, 30))
        font_brand = FontManager.get_font("black", 22)
        draw.text((cls.WIDTH // 2, 60), "WILD VAULT", font=font_brand, fill=(255, 255, 255), anchor="mm")
        font_subbrand = FontManager.get_font("bold", 14)
        draw.text((cls.WIDTH // 2, 82), "SCIENCE DISCOVERY", font=font_subbrand, fill=(255, 255, 255), anchor="mm")

        # 2. Degradado Inferior Profundo
        gradient = cls._create_dark_gradient(cls.WIDTH, cls.HEIGHT, start_y=680, max_alpha=240)
        canvas.paste(gradient, (0, 0), gradient)

        draw_grad = ImageDraw.Draw(canvas)
        font_news = FontManager.get_font("black", 48)

        # Envolver texto en líneas de 35 caracteres
        words = headline_text.split()
        lines = []
        cur_line = []
        for w in words:
            cur_line.append(w)
            if len(" ".join(cur_line)) > 28:
                lines.append(" ".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append(" ".join(cur_line))

        y_cursor = 860
        for l in lines[:5]:
            draw_grad.text((60, y_cursor), l, font=font_news, fill=(255, 255, 255))
            y_cursor += 65

        canvas.save(output_path, quality=95)
        return output_path

    # =========================================================================
    # FORMATO 8: Collage Cuádruple 2x2 (Titanes con Mirada Asesina)
    # =========================================================================
    @classmethod
    def render_format_8_quad_collage(
        cls,
        four_image_paths: List[Path],
        output_path: Path,
        overlay_title: Optional[str] = "4 TITANS OF NATURE"
    ) -> Path:
        canvas = Image.new("RGB", (cls.WIDTH, cls.HEIGHT), (10, 10, 12))
        half_w = cls.WIDTH // 2
        half_h = cls.HEIGHT // 2

        coords = [
            (0, 0),
            (half_w, 0),
            (0, half_h),
            (half_w, half_h)
        ]

        for idx, p in enumerate(four_image_paths[:4]):
            if Path(p).exists():
                with Image.open(p) as q_img:
                    q_img = ImageOps.fit(q_img.convert("RGB"), (half_w, half_h), method=Image.Resampling.LANCZOS)
                    canvas.paste(q_img, coords[idx])

        draw = ImageDraw.Draw(canvas)
        # Líneas de división limpias
        draw.line([(half_w, 0), (half_w, cls.HEIGHT)], fill=(20, 20, 20), width=6)
        draw.line([(0, half_h), (cls.WIDTH, half_h)], fill=(20, 20, 20), width=6)

        # Badge central
        if overlay_title:
            font_b = FontManager.get_font("black", 24)
            bw, bh = 460, 60
            bx = (cls.WIDTH - bw) // 2
            by = (cls.HEIGHT - bh) // 2
            draw.rectangle([(bx, by), (bx + bw, by + bh)], fill=(15, 15, 18), outline=(255, 215, 0), width=3)
            draw.text((cls.WIDTH // 2, cls.HEIGHT // 2), overlay_title.upper(), font=font_b, fill=(255, 255, 255), anchor="mm")

        canvas.save(output_path, quality=95)
        return output_path
