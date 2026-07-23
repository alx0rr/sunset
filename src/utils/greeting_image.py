from __future__ import annotations

import asyncio
import random
from io import BytesIO
from pathlib import Path
from typing import BinaryIO


import aiohttp
from PIL import Image, ImageDraw, ImageFont, ImageOps

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_DIR = BASE_DIR / "res" / "assets"
LOCALES_DIR = BASE_DIR / "res" / "locales"

BACKGROUNDS_DIR = ASSETS_DIR / "backgrounds"
FONT_PATH = ASSETS_DIR / "fonts" / "main.ttf"
DEFAULT_AVATAR_PATH = ASSETS_DIR / "default_avatar.jpg"

CANVAS_SIZE = (1000, 500)
AVATAR_SIZE = 220

_backgrounds: list[Image.Image] = []
_default_avatar: Image.Image | None = None
_font_cache: dict[int, ImageFont.FreeTypeFont] = {}


# ---------- warmup ----------

async def load_image_assets() -> None:
    """Load backgrounds and the default avatar into memory. Call once at startup."""
    global _default_avatar

    _backgrounds.clear()
    for path in sorted(BACKGROUNDS_DIR.iterdir()):
        if path.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        img = Image.open(path).convert("RGB")
        img = ImageOps.fit(img, CANVAS_SIZE, Image.LANCZOS)
        img.load()
        _backgrounds.append(img)

    if not _backgrounds:
        raise RuntimeError(f"No backgrounds found in {BACKGROUNDS_DIR}")

    avatar = Image.open(DEFAULT_AVATAR_PATH).convert("RGBA")
    avatar.load()
    _default_avatar = _circle(avatar, AVATAR_SIZE)


def _font(size: int) -> ImageFont.FreeTypeFont:
    if size not in _font_cache:
        _font_cache[size] = ImageFont.truetype(str(FONT_PATH), size)
    return _font_cache[size]


# ---------- helpers ----------

def _circle(img: Image.Image, size: int) -> Image.Image:
    img = ImageOps.fit(img.convert("RGBA"), (size, size), Image.LANCZOS)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    img.putalpha(mask)
    return img


async def _fetch_avatar(url: str) -> Image.Image | None:
    try:
        timeout = aiohttp.ClientTimeout(total=8)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    return None
                raw = await resp.read()
        img = Image.open(BytesIO(raw))
        img.load()
        return _circle(img, AVATAR_SIZE)
    except Exception:
        return None


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        probe = f"{current} {word}".strip()
        if draw.textlength(probe, font=font) <= max_width:
            current = probe
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:4]


# ---------- render ----------

def _render(text: str, avatar: Image.Image) -> BytesIO:
    canvas = random.choice(_backgrounds).copy()

    # затемняющий слой под текст
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 110))
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay)

    ax = (CANVAS_SIZE[0] - AVATAR_SIZE) // 2
    ay = 60

    ring = Image.new("RGBA", (AVATAR_SIZE + 12, AVATAR_SIZE + 12), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse(
        (0, 0, AVATAR_SIZE + 12, AVATAR_SIZE + 12), fill=(255, 255, 255, 230)
    )
    canvas.paste(ring, (ax - 6, ay - 6), ring)
    canvas.paste(avatar, (ax, ay), avatar)

    draw = ImageDraw.Draw(canvas)
    font = _font(46)
    lines = _wrap(draw, text, font, CANVAS_SIZE[0] - 120)

    y = ay + AVATAR_SIZE + 45
    for line in lines:
        w = draw.textlength(line, font=font)
        x = (CANVAS_SIZE[0] - w) / 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255),
                  stroke_width=3, stroke_fill=(0, 0, 0))
        y += font.size + 12

    buf = BytesIO()
    canvas.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    return buf


async def make_greeting_image(text: str, avatar_url: str | None) -> BinaryIO:
    avatar = None
    if avatar_url:
        avatar = await _fetch_avatar(avatar_url)
    if avatar is None:
        avatar = _default_avatar

    buf = await asyncio.to_thread(_render, text, avatar)
    buf.name = "greeting.png"   # чтобы mimetypes.guess_type отдал image/png
    return buf