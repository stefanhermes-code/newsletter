"""
Newsletter Generator Module

Generates HTML newsletters from selected articles with customer branding.
Supports category sections, intro/announcements, banners, and Short.io links.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import quote

import streamlit as st

from user_modules.banner_utils import banner_data_uri, enrich_banner
from user_modules.category_mapper import (
    assign_sections,
    draft_intro_from_articles,
    group_by_section,
    load_category_config,
    suggest_banner_theme,
)
from user_modules.github_user import get_repo, save_newsletter
from user_modules import shortio_client

logger = logging.getLogger(__name__)


def _load_logo_data_uri(logo_path: str) -> str:
    if not logo_path:
        return ""
    try:
        repo = get_repo()
        if repo:
            file = repo.get_contents(logo_path)
            content_b64 = file.content
            ext = logo_path.split(".")[-1].lower()
            mime = "image/png" if ext == "png" else "image/jpeg"
            return f"data:{mime};base64,{content_b64}"
        raise Exception("repo unavailable")
    except Exception:
        try:
            from pathlib import Path
            import base64

            local = Path(logo_path)
            if local.exists():
                ext = logo_path.split(".")[-1].lower()
                mime = "image/png" if ext == "png" else "image/jpeg"
                b64 = base64.b64encode(local.read_bytes()).decode("ascii")
                return f"data:{mime};base64,{b64}"
        except Exception:
            pass
        repo_name = st.secrets.get("github_repo", "") if hasattr(st, "secrets") else ""
        if repo_name:
            return f"https://raw.githubusercontent.com/{repo_name}/main/{quote(logo_path)}"
        return logo_path


def generate_newsletter(
    selected_articles: List[Dict],
    branding: Dict,
    customer_id: str,
    short_name: str = "",
    intro_text: str = "",
    announcements: str = "",
    use_shortio: bool = True,
) -> Optional[str]:
    """
    Generate newsletter HTML from selected articles and save to GitHub.
    """
    if not selected_articles:
        st.error("No articles selected for newsletter generation")
        return None

    application_name = branding.get("application_name", "Newsletter")
    newsletter_title_template = branding.get(
        "newsletter_title_template", "{name} - Week {week}"
    )
    footer_text = branding.get("footer_text", "")
    footer_url = branding.get("footer_url", "")
    footer_url_display = branding.get("footer_url_display", footer_url)
    logo_path = branding.get("logo_path", "")
    banner_path = branding.get("banner_path", "")
    if not banner_path:
        # Fall back to local branding or conventional asset path
        try:
            from pathlib import Path
            import json

            local_branding = Path(f"customers/{customer_id}/config/branding.json")
            if local_branding.exists():
                with open(local_branding, encoding="utf-8") as f:
                    banner_path = json.load(f).get("banner_path", "") or banner_path
            if not banner_path:
                candidate = Path(f"customers/{customer_id}/assets")
                if candidate.exists():
                    for p in candidate.glob("*Banner*.png"):
                        banner_path = str(p).replace("\\", "/")
                        break
        except Exception:
            pass

    week_number = datetime.now().isocalendar()[1]
    year = datetime.now().year
    campaign = f"{(short_name or customer_id).lower()}-week-{week_number:02d}-{year}"

    newsletter_title = newsletter_title_template.format(
        name=application_name, week=week_number
    )

    if short_name:
        filename = f"{short_name}_Week_{week_number:02d}_{year}.html"
    else:
        filename = f"Newsletter_Week_{week_number:02d}_{year}.html"

    category_config = load_category_config(customer_id)
    articles = assign_sections(selected_articles, category_config)

    if use_shortio and shortio_client.is_configured():
        # Best-effort cleanup of old links to free Free-plan quota
        try:
            deleted = shortio_client.cleanup_old_links(older_than_days=60, limit=100)
            if deleted:
                logger.info(f"Short.io cleanup deleted {deleted} old links")
        except Exception as e:
            logger.warning(f"Short.io cleanup skipped: {e}")

        articles, ok, failed = shortio_client.shorten_articles(
            articles,
            campaign=campaign,
            tag_prefix=(short_name or "newsletter").lower(),
            ttl_days=60,
        )
        if ok:
            st.info(f"Short.io: created {ok} tracked link(s) on {st.secrets.get('shortio_domain', '')}")
        if failed:
            st.warning(f"Short.io: {failed} link(s) could not be shortened; using original URLs.")

    logo_url = _load_logo_data_uri(logo_path)
    banner_url = banner_data_uri(banner_path) if banner_path else ""

    if not intro_text.strip():
        intro_text = draft_intro_from_articles(articles, category_config)

    html_content = format_html_newsletter(
        articles,
        newsletter_title,
        application_name,
        footer_text,
        footer_url,
        footer_url_display,
        logo_url=logo_url,
        banner_url=banner_url,
        intro_text=intro_text,
        announcements=announcements,
        category_config=category_config,
    )

    # Persist for UI download of LinkedIn cover
    theme = suggest_banner_theme(articles, category_config)
    if banner_path:
        enriched = enrich_banner(
            banner_path, week_number=week_number, year=year, theme=theme
        )
        if enriched:
            st.session_state["last_banner_png"], st.session_state["last_banner_filename"] = (
                enriched
            )
            st.session_state["last_banner_theme"] = theme

    st.session_state["last_newsletter_html"] = html_content
    st.session_state["last_newsletter_filename"] = filename

    try:
        success = save_newsletter(customer_id, html_content, filename)
        if success:
            logger.info(f"Newsletter saved: {filename}")
            return filename
        st.error("Failed to save newsletter to GitHub")
        return None
    except Exception as e:
        logger.error(f"Error saving newsletter: {e}")
        st.error(f"Error saving newsletter: {e}")
        return None


def format_html_newsletter(
    articles: List[Dict],
    title: str,
    application_name: str,
    footer_text: str,
    footer_url: str,
    footer_url_display: str,
    logo_url: str = "",
    banner_url: str = "",
    intro_text: str = "",
    announcements: str = "",
    category_config: Optional[Dict] = None,
) -> str:
    """Format newsletter as HTML with branding, intro, and category sections."""

    def esc(text: str) -> str:
        return (
            (text or "")
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    grouped = group_by_section(articles, category_config)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .newsletter-container {{
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .banner {{
            width: 100%;
            height: auto;
            display: block;
            border-radius: 6px;
            margin-bottom: 20px;
        }}
        .header {{
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 20px;
        }}
        .logo {{ height: 48px; }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 28px;
        }}
        .date-info {{
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
            margin-bottom: 20px;
        }}
        .intro {{
            background: #f8fafc;
            border-left: 4px solid #2c3e50;
            padding: 14px 16px;
            margin-bottom: 18px;
            color: #334155;
            font-size: 15px;
        }}
        .announcements {{
            background: #fff7ed;
            border-left: 4px solid #ea580c;
            padding: 14px 16px;
            margin-bottom: 28px;
            color: #9a3412;
            font-size: 15px;
        }}
        .announcements h2, .intro h2 {{
            margin: 0 0 8px 0;
            font-size: 16px;
            color: inherit;
        }}
        .category-section {{
            margin-top: 28px;
            margin-bottom: 8px;
        }}
        .category-section h2 {{
            margin: 0 0 14px 0;
            font-size: 18px;
            color: #1e293b;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 6px;
        }}
        .article {{
            margin-bottom: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .article-title {{
            font-size: 17px;
            font-weight: bold;
            color: #2c3e50;
            line-height: 1.4;
        }}
        .article-title a {{
            color: #2c3e50;
            text-decoration: none;
        }}
        .article-title a:hover {{
            color: #3498db;
            text-decoration: underline;
        }}
        .article-meta {{
            font-size: 12px;
            color: #7f8c8d;
            font-weight: normal;
            white-space: nowrap;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            font-size: 12px;
            color: #7f8c8d;
        }}
        .footer a {{
            color: #3498db;
            text-decoration: none;
        }}
        .footer a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="newsletter-container">
        {f'<img class="banner" src="{banner_url}" alt="Newsletter banner" />' if banner_url else ''}
        <div class="header">
            {f'<img class="logo" src="{logo_url}" alt="logo" />' if logo_url else ''}
            <div>
                <h1 style="margin:0;">{esc(title)}</h1>
            </div>
        </div>

        <div class="date-info">
            Generated on {datetime.now().strftime("%B %d, %Y")}
        </div>
"""

    if intro_text.strip():
        paras = "".join(
            f"<p style=\"margin:0 0 8px 0;\">{esc(p.strip())}</p>"
            for p in intro_text.strip().split("\n")
            if p.strip()
        )
        html += f"""
        <div class="intro">
            <h2>In this issue</h2>
            {paras}
        </div>
"""

    if announcements.strip():
        paras = "".join(
            f"<p style=\"margin:0 0 8px 0;\">{esc(p.strip())}</p>"
            for p in announcements.strip().split("\n")
            if p.strip()
        )
        html += f"""
        <div class="announcements">
            <h2>APBA announcements &amp; upcoming events</h2>
            {paras}
        </div>
"""

    for section, section_articles in grouped.items():
        html += f"""
        <div class="category-section">
            <h2>{esc(section)}</h2>
"""
        for article in section_articles:
            article_title = esc(article.get("title", "No Title"))
            article_url = article.get("url", "#")
            article_date = esc(article.get("published_date", ""))
            date_span = (
                f' <span class="article-meta">· {article_date}</span>'
                if article_date
                else ""
            )
            html += f"""
            <div class="article">
                <div class="article-title">
                    <a href="{article_url}" target="_blank">{article_title}</a>{date_span}
                </div>
            </div>
"""
        html += """
        </div>
"""

    html += f"""
        <div class="footer">
            <p>{esc(footer_text)}</p>
            {f'<p><a href="{footer_url}" target="_blank">{esc(footer_url_display)}</a></p>' if footer_url else ''}
        </div>
    </div>
</body>
</html>
"""
    return html


def download_newsletter(html_content: str, filename: str):
    """Provide download button for newsletter HTML."""
    st.download_button(
        label="📥 Download Newsletter",
        data=html_content,
        file_name=filename,
        mime="text/html",
        key=f"download_{filename}",
    )


def download_linkedin_banner():
    """Offer LinkedIn cover download if an enriched banner is in session."""
    png = st.session_state.get("last_banner_png")
    name = st.session_state.get("last_banner_filename")
    if not png or not name:
        return
    st.download_button(
        label="🖼️ Download LinkedIn cover (week-enriched)",
        data=png,
        file_name=name,
        mime="image/png",
        key=f"download_banner_{name}",
    )


def get_newsletter_preview(
    selected_articles: List[Dict],
    branding: Dict,
    customer_id: str = "",
    intro_text: str = "",
    announcements: str = "",
) -> str:
    """Generate preview HTML for newsletter (without saving / without Short.io)."""
    application_name = branding.get("application_name", "Newsletter")
    newsletter_title_template = branding.get(
        "newsletter_title_template", "{name} - Week {week}"
    )
    week_number = datetime.now().isocalendar()[1]
    newsletter_title = newsletter_title_template.format(
        name=application_name, week=week_number
    )
    footer_text = branding.get("footer_text", "")
    footer_url = branding.get("footer_url", "")
    footer_url_display = branding.get("footer_url_display", footer_url)
    logo_path = branding.get("logo_path", "")
    banner_path = branding.get("banner_path", "")

    category_config = load_category_config(customer_id) if customer_id else None
    articles = (
        assign_sections(selected_articles, category_config)
        if category_config
        else selected_articles
    )
    if not intro_text.strip() and category_config:
        intro_text = draft_intro_from_articles(articles, category_config)

    return format_html_newsletter(
        articles,
        newsletter_title,
        application_name,
        footer_text,
        footer_url,
        footer_url_display,
        logo_url=_load_logo_data_uri(logo_path) if logo_path else "",
        banner_url=banner_data_uri(banner_path) if banner_path else "",
        intro_text=intro_text,
        announcements=announcements,
        category_config=category_config,
    )
