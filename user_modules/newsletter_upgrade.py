"""
Upgrade legacy newsletter HTML to the new categorized format.
"""

from __future__ import annotations

import logging
import re
from html import unescape
from typing import Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from user_modules.category_mapper import (
    assign_sections,
    draft_intro_from_articles,
    load_category_config,
    resolve_section,
)

logger = logging.getLogger(__name__)


def is_new_format(html: str) -> bool:
    """Heuristic: new format has category sections and/or intro block."""
    if not html:
        return False
    return 'class="category-section"' in html or 'class="intro"' in html


def parse_newsletter_html(html: str) -> Tuple[List[Dict], Dict]:
    """
    Extract articles and metadata from old or new newsletter HTML.

    Returns:
        (articles, meta) where meta may include title, generated_on
    """
    soup = BeautifulSoup(html or "", "html.parser")
    meta: Dict = {}

    title_tag = soup.find("title")
    if title_tag and title_tag.get_text(strip=True):
        meta["title"] = title_tag.get_text(strip=True)
    h1 = soup.select_one(".header h1")
    if h1 and h1.get_text(strip=True):
        meta["title"] = h1.get_text(strip=True)

    date_info = soup.select_one(".date-info")
    if date_info:
        meta["generated_on"] = date_info.get_text(strip=True)

    articles: List[Dict] = []

    # Prefer structured category sections (new format)
    sections = soup.select(".category-section")
    if sections:
        for section in sections:
            heading = section.find("h2")
            section_name = heading.get_text(strip=True) if heading else "Other"
            for art in section.select(".article"):
                parsed = _parse_article_block(art)
                if parsed:
                    parsed["newsletter_section"] = section_name
                    parsed["category"] = section_name
                    articles.append(parsed)
        return articles, meta

    # Legacy flat list
    for art in soup.select(".article"):
        parsed = _parse_article_block(art)
        if parsed:
            articles.append(parsed)

    return articles, meta


def _parse_article_block(art) -> Optional[Dict]:
    link = art.select_one(".article-title a") or art.find("a")
    if not link:
        return None
    title = unescape(link.get_text(strip=True) or "")
    url = link.get("href") or "#"
    if not title:
        return None

    date = ""
    meta_el = art.select_one(".article-meta")
    if meta_el:
        raw = meta_el.get_text(" ", strip=True)
        date = re.sub(r"^[📅\s·]+", "", raw).strip()
    else:
        # Inline date after link: " · 2026-07-14"
        title_div = art.select_one(".article-title")
        if title_div:
            full = title_div.get_text(" ", strip=True)
            m = re.search(r"·\s*(\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2},\s*\d{4})", full)
            if m:
                date = m.group(1)

    return {
        "title": title,
        "url": url,
        "published_date": date,
        "source": "",
        "snippet": "",
        "category": "",
        "found_via": "upgrade",
    }


def infer_keyword_categories(
    articles: List[Dict],
    all_keywords: List[str],
    category_config: Dict,
) -> List[Dict]:
    """
    Assign newsletter sections by matching article titles to configured keywords.
    Longest keyword match wins. Falls back to existing section or Other.
    """
    mappings = category_config.get("keyword_mappings") or {}
    categories = category_config.get("categories") or []
    keywords_sorted = sorted([k for k in all_keywords if k], key=len, reverse=True)

    result = []
    for article in articles:
        item = dict(article)
        # Keep explicit section from new-format HTML if present
        if item.get("newsletter_section") and item["newsletter_section"] in (
            categories or [item["newsletter_section"]]
        ):
            if not item.get("category"):
                item["category"] = item["newsletter_section"]
            result.append(item)
            continue

        title_l = (item.get("title") or "").lower()
        matched_kw = ""
        for kw in keywords_sorted:
            if kw.lower() in title_l:
                matched_kw = kw
                break

        if matched_kw:
            item["category"] = matched_kw
            item["newsletter_section"] = resolve_section(
                matched_kw, mappings, categories
            )
        else:
            item["category"] = item.get("category") or "Other"
            item["newsletter_section"] = resolve_section(
                item["category"], mappings, categories
            )
        result.append(item)

    # Normalize via assign_sections for consistency
    return assign_sections(result, category_config)


def upgrade_html_content(
    html: str,
    *,
    customer_id: str,
    branding: Dict,
    all_keywords: Optional[List[str]] = None,
    intro_text: str = "",
    announcements: str = "",
    use_shortio: bool = False,
) -> Tuple[Optional[str], List[Dict], Dict]:
    """
    Parse legacy HTML and rebuild with the new template.

    Returns: (new_html, articles, meta) — new_html is None if no articles found.
    """
    from user_modules.newsletter_generator import (
        _load_logo_data_uri,
        format_html_newsletter,
    )
    from user_modules.banner_utils import banner_data_uri, enrich_banner
    from user_modules.category_mapper import suggest_banner_theme as theme_fn
    from datetime import datetime
    from pathlib import Path
    import json

    articles, meta = parse_newsletter_html(html)
    if not articles:
        return None, [], meta

    category_config = load_category_config(customer_id)
    keywords = all_keywords or []
    articles = infer_keyword_categories(articles, keywords, category_config)

    if not intro_text.strip():
        intro_text = draft_intro_from_articles(articles, category_config)

    if use_shortio:
        try:
            from user_modules import shortio_client

            if shortio_client.is_configured():
                short_name = branding.get("short_name") or customer_id
                week_number = datetime.now().isocalendar()[1]
                year = datetime.now().year
                # Prefer week from original title if present
                title_src = meta.get("title") or ""
                wm = re.search(r"Week\s+(\d+)", title_src, re.I)
                if wm:
                    week_number = int(wm.group(1))
                campaign = f"{short_name.lower()}-week-{week_number:02d}-{year}-upgrade"
                articles, _, _ = shortio_client.shorten_articles(
                    articles, campaign=campaign, tag_prefix=short_name.lower(), ttl_days=60
                )
        except Exception as e:
            logger.warning(f"Short.io during upgrade skipped: {e}")

    application_name = branding.get("application_name", "Newsletter")
    newsletter_title = meta.get("title") or branding.get(
        "newsletter_title_template", "{name} - Week {week}"
    ).format(name=application_name, week=datetime.now().isocalendar()[1])

    logo_path = branding.get("logo_path", "")
    banner_path = branding.get("banner_path", "")
    if not banner_path:
        try:
            local_branding = Path(f"customers/{customer_id}/config/branding.json")
            if local_branding.exists():
                with open(local_branding, encoding="utf-8") as f:
                    banner_path = json.load(f).get("banner_path", "") or banner_path
            if not banner_path:
                assets = Path(f"customers/{customer_id}/assets")
                if assets.exists():
                    for p in assets.glob("*Banner*.png"):
                        banner_path = str(p).replace("\\", "/")
                        break
        except Exception:
            pass

    new_html = format_html_newsletter(
        articles,
        newsletter_title,
        application_name,
        branding.get("footer_text", ""),
        branding.get("footer_url", ""),
        branding.get("footer_url_display", branding.get("footer_url", "")),
        logo_url=_load_logo_data_uri(logo_path) if logo_path else "",
        banner_url=banner_data_uri(banner_path) if banner_path else "",
        intro_text=intro_text,
        announcements=announcements,
        category_config=category_config,
    )

    # Optional LinkedIn cover into session (caller may expose download)
    try:
        import streamlit as st

        theme = theme_fn(articles, category_config)
        if banner_path:
            wm = re.search(r"Week\s+(\d+)", newsletter_title, re.I)
            week_number = int(wm.group(1)) if wm else datetime.now().isocalendar()[1]
            year = datetime.now().year
            enriched = enrich_banner(
                banner_path, week_number=week_number, year=year, theme=theme
            )
            if enriched:
                st.session_state["last_banner_png"], st.session_state["last_banner_filename"] = (
                    enriched
                )
    except Exception:
        pass

    return new_html, articles, meta
