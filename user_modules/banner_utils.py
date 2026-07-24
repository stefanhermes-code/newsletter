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
        # Fallback public raw URL
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


def enrich_banner(
    banner_path: str,
    *,
    week_number: Optional[int] = None,
    year: Optional[int] = None,
    theme: str = "",
) -> Optional[Tuple[bytes, str]]:
    """
    Overlay week + optional theme on the banner for LinkedIn upload.

    Returns (png_bytes, filename) or None.
    """
    raw = load_banner_bytes(banner_path)
    if not raw:
        return None

    try:
        from PIL import Image, ImageDraw, ImageFont
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

        # Prefer a clean sans font; fall back to default
        font_large = None
        font_small = None
        for name in (
            "C:/Windows/Fonts/arialbd.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ):
            try:
                font_large = ImageFont.truetype(name, max(28, w // 40))
                font_small = ImageFont.truetype(name, max(20, w // 55))
                break
            except Exception:
                continue
        if font_large is None:
            font_large = ImageFont.load_default()
            font_small = font_large

        line1 = f"WEEK {week_number:02d} · {year}"
        line2 = theme.strip() if theme else ""

        # Lower-left open area of the APBA banner
        margin_x = int(w * 0.04)
        margin_y = int(h * 0.72)
        padding = 14

        # Measure text block
        bbox1 = draw.textbbox((0, 0), line1, font=font_large)
        tw1, th1 = bbox1[2] - bbox1[0], bbox1[3] - bbox1[1]
        tw2 = th2 = 0
        if line2:
            bbox2 = draw.textbbox((0, 0), line2, font=font_small)
            tw2, th2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]

        box_w = max(tw1, tw2) + padding * 2
        box_h = th1 + (th2 + 8 if line2 else 0) + padding * 2

        # Semi-transparent dark plate for readability
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)
        odraw.rounded_rectangle(
            [margin_x, margin_y, margin_x + box_w, margin_y + box_h],
            radius=8,
            fill=(10, 25, 50, 170),
        )
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

        draw.text(
            (margin_x + padding, margin_y + padding),
            line1,
            fill=(255, 255, 255, 255),
            font=font_large,
        )
        if line2:
            draw.text(
                (margin_x + padding, margin_y + padding + th1 + 8),
                line2,
                fill=(255, 200, 120, 255),
                font=font_small,
            )

        out = io.BytesIO()
        img.convert("RGB").save(out, format="PNG", optimize=True)
        filename = f"APBA_LinkedIn_Cover_Week_{week_number:02d}_{year}.png"
        return out.getvalue(), filename
    except Exception as e:
        logger.error(f"Banner enrich failed: {e}")
        return None
