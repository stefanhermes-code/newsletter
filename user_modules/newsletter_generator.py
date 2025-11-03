"""
Newsletter Generator Module

Generates HTML newsletters from selected articles with customer branding.
Direct generation (no draft step).
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
from user_modules.github_user import save_newsletter, get_repo
import base64
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

def generate_newsletter(selected_articles: List[Dict], branding: Dict, customer_id: str, 
                       short_name: str = "") -> Optional[str]:
    """
    Generate newsletter HTML from selected articles
    
    Args:
        selected_articles: List of selected article dictionaries
        branding: Customer branding configuration
        customer_id: Customer identifier
        short_name: Short name for file naming (e.g., 'HTC', 'APBA')
    
    Returns:
        Newsletter HTML string, or None if error
    """
    if not selected_articles:
        st.error("No articles selected for newsletter generation")
        return None
    
    # Get branding settings
    application_name = branding.get("application_name", "Newsletter")
    newsletter_title_template = branding.get("newsletter_title_template", "{name} - Week {week}")
    footer_text = branding.get("footer_text", "")
    footer_url = branding.get("footer_url", "")
    footer_url_display = branding.get("footer_url_display", footer_url)
    logo_path = branding.get("logo_path", "")
    
    # Calculate week number
    week_number = datetime.now().isocalendar()[1]
    year = datetime.now().year
    
    # Generate newsletter title
    newsletter_title = newsletter_title_template.format(
        name=application_name,
        week=week_number
    )
    
    # Generate filename
    if short_name:
        filename = f"{short_name}_Week_{week_number:02d}_{year}.html"
    else:
        filename = f"Newsletter_Week_{week_number:02d}_{year}.html"
    
    # Build HTML
    # Build a data URI or raw URL for the logo so it renders in preview/email
    logo_url = ""
    if logo_path:
        # Try to fetch the logo content from GitHub to embed as data URI (works for private repos)
        try:
            repo = get_repo()
            if repo:
                file = repo.get_contents(logo_path)
                content_b64 = file.content  # already base64
                # Guess mime
                ext = logo_path.split('.')[-1].lower()
                mime = 'image/png' if ext in ('png',) else 'image/jpeg'
                logo_url = f"data:{mime};base64,{content_b64}"
            else:
                raise Exception("repo unavailable")
        except Exception:
            # Fallback to public raw link (only works for public repos)
            repo_name = st.secrets.get("github_repo", "") if hasattr(st, 'secrets') else ""
            if repo_name:
                logo_url = f"https://raw.githubusercontent.com/{repo_name}/main/{quote(logo_path)}"
            else:
                logo_url = logo_path

    html_content = format_html_newsletter(
        selected_articles,
        newsletter_title,
        application_name,
        footer_text,
        footer_url,
        footer_url_display,
        logo_url
    )
    
    # Save to GitHub
    try:
        success = save_newsletter(customer_id, html_content, filename)
        if success:
            logger.info(f"Newsletter saved: {filename}")
            return filename
        else:
            st.error("Failed to save newsletter to GitHub")
            return None
    except Exception as e:
        logger.error(f"Error saving newsletter: {e}")
        st.error(f"Error saving newsletter: {e}")
        return None

def format_html_newsletter(articles: List[Dict], title: str, application_name: str,
                          footer_text: str, footer_url: str, footer_url_display: str,
                          logo_url: str = "") -> str:
    """
    Format newsletter as HTML with branding
    
    Args:
        articles: List of article dictionaries
        title: Newsletter title
        application_name: Application name for branding
        footer_text: Footer text
        footer_url: Footer URL
        footer_url_display: Footer URL display text
    
    Returns:
        Complete HTML string
    """
    # HTML header with styling
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
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
        .header {{
            display: flex;
            align-items: center;
            gap: 12px;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .logo {{ height: 48px; }}
        .header h1 {{
            color: #2c3e50;
            margin: 0;
            font-size: 28px;
        }}
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 14px;
            margin-top: 5px;
        }}
        .article {{
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .article:last-child {{
            border-bottom: none;
        }}
        .article-title {{
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
            color: #2c3e50;
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
            margin-bottom: 10px;
        }}
        .article-snippet {{
            color: #555;
            margin-top: 10px;
            line-height: 1.6;
        }}
        .article-link {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background-color: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 14px;
        }}
        .article-link:hover {{
            background-color: #2980b9;
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
        .date-info {{
            text-align: center;
            color: #7f8c8d;
            font-size: 12px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="newsletter-container">
        <div class="header">
            {f'<img class="logo" src="{logo_url}" alt="logo" />' if logo_url else ''}
            <div>
                <h1 style="margin:0;">{title}</h1>
                <div class="subtitle">{application_name}</div>
            </div>
        </div>
        
        <div class="date-info">
            Generated on {datetime.now().strftime("%B %d, %Y")}
        </div>
"""
    
    # Add articles
    for idx, article in enumerate(articles, 1):
        article_title = article.get('title', 'No Title')
        article_url = article.get('url', '#')
        article_source = article.get('source', 'Unknown')
        article_date = article.get('published_date', '')
        article_snippet = article.get('snippet', '')
        
        html += f"""
        <div class="article">
            <div class="article-title">
                <a href="{article_url}" target="_blank">{article_title}</a>
            </div>
            <div class="article-meta">
                📰 {article_source} | 📅 {article_date}
            </div>
            {f'<div class="article-snippet">{article_snippet}</div>' if article_snippet else ''}
            <a href="{article_url}" target="_blank" class="article-link">Read Full Article →</a>
        </div>
"""
    
    # Add footer
    html += f"""
        <div class="footer">
            <p>{footer_text}</p>
            {f'<p><a href="{footer_url}" target="_blank">{footer_url_display}</a></p>' if footer_url else ''}
        </div>
    </div>
</body>
</html>
"""
    
    return html

def download_newsletter(html_content: str, filename: str):
    """
    Provide download button for newsletter HTML
    
    Args:
        html_content: Newsletter HTML content
        filename: Filename for download
    """
    st.download_button(
        label="📥 Download Newsletter",
        data=html_content,
        file_name=filename,
        mime="text/html",
        key=f"download_{filename}"
    )

def get_newsletter_preview(selected_articles: List[Dict], branding: Dict) -> str:
    """
    Generate preview HTML for newsletter (without saving)
    
    Args:
        selected_articles: List of selected articles
        branding: Branding configuration
    
    Returns:
        Preview HTML string
    """
    application_name = branding.get("application_name", "Newsletter")
    newsletter_title_template = branding.get("newsletter_title_template", "{name} - Week {week}")
    
    week_number = datetime.now().isocalendar()[1]
    newsletter_title = newsletter_title_template.format(
        name=application_name,
        week=week_number
    )
    
    footer_text = branding.get("footer_text", "")
    footer_url = branding.get("footer_url", "")
    footer_url_display = branding.get("footer_url_display", footer_url)
    
    return format_html_newsletter(
        selected_articles,
        newsletter_title,
        application_name,
        footer_text,
        footer_url,
        footer_url_display
    )

