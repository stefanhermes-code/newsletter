"""
Banner image helpers: embed in newsletter HTML and enrich for LinkedIn download.
"""

from __future__ import annotations

import base64
import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import quote

import streamlit as st

logger = logging.getLogger(__name__)


def _guess_mime(path: str) -> str:
    ext = path.split(".")[-1].lower()
    if ext in ("jpg", "jpeg"):
        return "image/jpeg"
    if ext == "webp":
        return "image/webp"
    return "image/png"


def load_banner_bytes(banner_path: str) -> Optional[bytes]:
    """Load banner from local path or GitHub."""
    if not banner_path:
        return None

    local = Path(banner_path)
    if local.exists():
        try:
            return local.read_bytes()
        except Exception as e:
            logger.warning(f"Could not read local banner: {e}")

    try:
        from user_modules.github_user import get_repo

        repo = get_repo()
        if repo:
            file = repo.get_contents(banner_path)
            return base64.b64decode(file.content)
    except Exception as e:
        logger.warning(f"Could not load banner from GitHub: {e}")

    return None


def banner_data_uri(banner_path: str) -> str:
    """Return data URI for newsletter HTML, or empty string."""
    data = load_banner_bytes(banner_path)
    if not data:
        try:
            repo_name = st.secrets.get("github_repo", "") if hasattr(st, "secrets") else ""
            if repo_name and banner_path:
                return f"https://raw.githubusercontent.com/{repo_name}/main/{quote(banner_path)}"
        except Exception:
            pass
        return ""
    mime = _guess_mime(banner_path)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _avg_brightness(img, box) -> float:
    crop = img.crop(box).convert("L")
    pixels = list(crop.getdata())
    return (sum(pixels) / len(pixels)) if pixels else 0.0


def _load_font(size: int):
    from PIL import ImageFont

    for name in (
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            continue
    return ImageFont.load_default()


def enrich_banner(
    banner_path: str,
    *,
    week_number: Optional[int] = None,
    year: Optional[int] = None,
    theme: str = "",
) -> Optional[Tuple[bytes, str]]:
    """
    Overlay a clear week line (+ optional theme) without covering APBA branding.

    Supports:
    - Wide layout with white APBA panel on the left (preferred LinkedIn cover)
    - Full-bleed dark banners with logo bottom-right
    """
    raw = load_banner_bytes(banner_path)
    if not raw:
        return None

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        logger.error("Pillow not installed; cannot enrich banner")
        return None

    if week_number is None:
        week_number = datetime.now().isocalendar()[1]
    if year is None:
        year = datetime.now().year

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGBA")
        draw = ImageDraw.Draw(img)
        w, h = img.size

        aspect = w / float(h)

        # Find where the dark content panel begins (skip white APBA brand panel if present)
        gray = img.convert("L")
        dark_start = 0
        for x in range(0, w, 5):
            col = [gray.getpixel((x, y)) for y in range(0, h, 8)]
            if (sum(col) / len(col)) < 45:
                # Confirm a stretch of dark columns (not just a black letter)
                confirm = []
                for xx in range(x, min(w, x + 80), 5):
                    c2 = [gray.getpixel((xx, y)) for y in range(0, h, 8)]
                    confirm.append(sum(c2) / len(c2))
                if confirm and (sum(confirm) / len(confirm)) < 55:
                    dark_start = x
                    break
        brand_left = dark_start > int(w * 0.25) or aspect > 2.5
        if dark_start < int(w * 0.25):
            dark_start = int(w * 0.45) if brand_left else int(w * 0.08)

        font_week = _load_font(max(22, h // 12))
        font_theme = _load_font(max(16, h // 18))

        line1 = f"WEEK {week_number:02d}  ·  {year}"
        line2 = (theme or "").strip()

        # Anchor text in the dark content area only (never over the white APBA panel)
        if brand_left:
            text_left = dark_start + max(16, w // 80)
            cy = int(h * 0.68)
            max_text_w = w - text_left - max(20, w // 40)
            center_mode = False
            cx = text_left
        else:
            text_left = int(w * 0.08)
            cy = int(h * 0.62)
            max_text_w = int(w * 0.55)
            center_mode = True
            cx = int(w * 0.42)

        def _draw_line(text, font, y, fill):
            bbox = draw.textbbox((0, 0), text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
            display = text
            if tw > max_text_w and len(text) > 28:
                display = text[:28].rstrip() + "…"
                bbox = draw.textbbox((0, 0), display, font=font)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
            if center_mode:
                x = cx - tw // 2
            else:
                x = text_left
            draw.text((x + 2, y + 2), display, fill=(0, 0, 0, 180), font=font)
            draw.text((x, y), display, fill=fill, font=font)
            return th

        th1 = _draw_line(line1, font_week, cy, (255, 176, 64, 255))  # amber pulse color
        if line2:
            _draw_line(line2, font_theme, cy + th1 + max(6, h // 40), (255, 255, 255, 255))

        out = io.BytesIO()
        img.convert("RGB").save(out, format="PNG", optimize=True)
        filename = f"APBA_LinkedIn_Cover_Week_{week_number:02d}_{year}.png"
        return out.getvalue(), filename
    except Exception as e:
        logger.error(f"Banner enrich failed: {e}")
        return None
