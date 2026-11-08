"""Clash of Clans art for HTML mails: fan kit icons and text in the Clash font.

Gmail ignores web fonts, so titles and big numbers are drawn as PNGs in the
dashboard's Clash font, white with a dark outline like in-game. Those and the
fan kit icons (coc-dashboard/public/icons, unmodified) travel inside the mail
as cid: images, so nothing is loaded from the web. Previews write them as
files next to the .html instead.
"""

import functools
import hashlib
import html
import io
import math
import os

from PIL import Image, ImageDraw, ImageFont

from config import REPO_ROOT

ICON_DIR = os.path.join(REPO_ROOT, "coc-dashboard", "public", "icons")
FONT_FILE = os.path.join(REPO_ROOT, "coc-dashboard", "app", "fonts", "Clash-Regular.otf")
OUTLINE = (27, 18, 8)  # --coc-outline in the dashboard's theme.css
WHITE = (255, 255, 255)
GOLD = (255, 216, 74)  # --coc-gold
SCALE = 2  # drawn at twice the display size, so text stays sharp on phones


@functools.lru_cache(maxsize=None)
def text_png(text: str, size: int, color: tuple) -> tuple[bytes, int, int]:
    """PNG of text in the Clash font with outline and drop; returns (png, width, height) at 1x."""
    font = ImageFont.truetype(FONT_FILE, size * SCALE)
    stroke = max(2, round(size * SCALE * 0.1))
    drop = max(1, round(size * SCALE * 0.08))
    # Letter by letter with the stroke width as extra spacing: Pillow strokes
    # around the glyph, which otherwise makes neighbouring letters merge
    spacing = stroke
    _, top, _, bottom = font.getbbox(text, stroke_width=stroke)
    advances = [font.getlength(ch) + spacing for ch in text]
    width = math.ceil(sum(advances) - spacing + 2 * stroke)
    height = bottom - top + drop
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for offset, fill in ((drop, OUTLINE), (0, color)):
        x = stroke
        for ch, advance in zip(text, advances):
            draw.text((x, -top + offset), ch, font=font, fill=fill, stroke_width=stroke, stroke_fill=OUTLINE)
            x += advance
    buffer = io.BytesIO()
    image.save(buffer, "PNG", optimize=True)
    return buffer.getvalue(), math.ceil(width / SCALE), math.ceil(height / SCALE)


class MailArt:
    """Collects the images one mail uses and hands out <img> tags for them."""

    def __init__(self, preview_dir: str | None = None):
        self.preview_dir = preview_dir
        self.images: dict[str, bytes] = {}  # cid -> PNG

    def _src(self, name: str, data: bytes) -> str:
        self.images[name] = data
        if not self.preview_dir:
            return f"cid:{name}"
        os.makedirs(os.path.join(self.preview_dir, "img"), exist_ok=True)
        with open(os.path.join(self.preview_dir, "img", name), "wb") as f:
            f.write(data)
        return f"img/{name}"

    def icon(self, name: str, size: int, alt: str = "") -> str:
        with open(os.path.join(ICON_DIR, f"{name}.png"), "rb") as f:
            src = self._src(f"{name}.png", f.read())
        return (f'<img src="{src}" width="{size}" height="{size}" alt="{html.escape(alt)}" '
                f'style="vertical-align:middle;border:0">')

    def text(self, text: str, size: int, color: tuple = WHITE) -> str:
        data, width, height = text_png(text, size, color)
        name = "t" + hashlib.sha1(f"{text}|{size}|{color}".encode()).hexdigest()[:12] + ".png"
        src = self._src(name, data)
        return (f'<img src="{src}" width="{width}" height="{height}" alt="{html.escape(text)}" '
                f'style="vertical-align:middle;border:0">')
