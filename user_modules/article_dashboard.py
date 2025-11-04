"""
Article Dashboard Module

Displays articles, provides preview functionality, and handles article selection
for newsletter generation.
"""

import streamlit as st
from typing import List, Dict, Optional
from datetime import datetime, date
import re
from user_modules.news_finder import get_article_content
import logging

logger = logging.getLogger(__name__)

def display_articles(articles: List[Dict], selected_article_ids: Optional[set] = None) -> set:
    """
    Display articles in a dashboard format with selection checkboxes
    
    Args:
        articles: List of article dictionaries
        selected_article_ids: Set of currently selected article IDs
    
    Returns:
        Updated set of selected article IDs
    """
    if selected_article_ids is None:
        selected_article_ids = st.session_state.get('selected_article_ids', set())
    
    if not articles:
        st.info("No articles found. Try adjusting your search criteria.")
        return selected_article_ids
    
    # Initialize selected articles in session state if needed
    # Always preserve existing selections - don't overwrite them
    if 'selected_article_ids' not in st.session_state:
        st.session_state.selected_article_ids = selected_article_ids.copy() if selected_article_ids else set()
    # Ensure we're working with a set (not accidentally resetting it)
    if not isinstance(st.session_state.selected_article_ids, set):
        st.session_state.selected_article_ids = set(st.session_state.selected_article_ids)
    
    st.write(f"**Found {len(articles)} articles**")
    
    # Filters (professional layout): keywords wide + date range side-by-side on the right
    col_kw, col_from, col_to = st.columns([4, 2, 2])
    
    with col_kw:
        # Build dropdown options from article categories (Google: matched keyword)
        keyword_options = sorted({a.get("category", "").strip() for a in articles if a.get("category")})
        selected_keywords = st.multiselect(
            "Keyword(s)",
            options=keyword_options,
            default=[],
            key="article_filter_keywords_multi",
            help="Select one or more keywords"
        )
    
    # Determine default bounds from data
    dates = []
    for a in articles:
        # Try ISO first (published_datetime), then YYYY-MM-DD
        dt_iso = a.get("published_datetime", "")
        if dt_iso:
            try:
                dates.append(datetime.fromisoformat(dt_iso).date())
                continue
            except Exception:
                pass
        d_plain = a.get("published_date", "")
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
            try:
                dates.append(datetime.strptime(d_plain, fmt).date())
                break
            except Exception:
                continue
    min_date = min(dates) if dates else None
    max_date = max(dates) if dates else None
    
    with col_from:
        start_date = st.date_input("From", value=min_date if min_date else date.today(), key="filter_from_date")
    with col_to:
        end_date = st.date_input("To", value=max_date if max_date else date.today(), key="filter_to_date")
    
    # Apply filters
    filtered_articles = articles
    # Date range apply
    if start_date and end_date:
        def in_range(a: Dict) -> bool:
            d = None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
                try:
                    d = datetime.strptime(a.get("published_date", ""), fmt).date()
                    break
                except Exception:
                    continue
            # fallback try isoformat from published_datetime
            if d is None:
                try:
                    d = datetime.fromisoformat(a.get("published_datetime", "")).date()
                except Exception:
                    return True  # if unknown, don't exclude
            return start_date <= d <= end_date
        filtered_articles = [a for a in filtered_articles if in_range(a)]
    
    # Keyword dropdown apply (match category)
    if selected_keywords:
        selected_set = set(k.lower() for k in selected_keywords)
        filtered_articles = [
            a for a in filtered_articles
            if a.get("category") and a.get("category").lower() in selected_set
        ]
    
    st.write(f"**Showing {len(filtered_articles)} articles** (filtered)")

    # Selection controls - inline, left-aligned
    # Note: "Select All" only selects currently visible (filtered) articles
    # Previously selected articles that are now filtered out remain selected
    btn_col1, btn_col2, _ = st.columns([1, 1, 8])
    with btn_col1:
        if st.button("Select All", key="select_all_articles"):
            # Add all filtered articles to selection (don't replace - add to existing)
            for article in filtered_articles:
                st.session_state.selected_article_ids.add(article.get("article_id", ""))
            st.rerun()
    with btn_col2:
        if st.button("Clear Selection", key="clear_selection"):
            st.session_state.selected_article_ids = set()
            st.rerun()
    
    st.markdown("---")
    
    # Display articles
    for idx, article in enumerate(filtered_articles):
        article_id = article.get("article_id", str(idx))
        # Always read current state from session state (not from previous render)
        is_selected = article_id in st.session_state.selected_article_ids
        
        # Article card
        with st.container():
            col1, col2 = st.columns([1, 10])
            
            with col1:
                # Checkbox for selection - always use session state as source of truth
                selected = st.checkbox(
                    "",
                    value=is_selected,
                    key=f"article_checkbox_{article_id}"
                )
                
                # Update session state if checkbox state changed
                # Read current session state again to avoid race conditions
                currently_selected = article_id in st.session_state.selected_article_ids
                if selected != currently_selected:
                    if selected:
                        st.session_state.selected_article_ids.add(article_id)
                    else:
                        st.session_state.selected_article_ids.discard(article_id)
                    # Reflect selection changes immediately (updates count above)
                    st.rerun()
            
            with col2:
                # Article info: Title as hyperlink, published date only
                title = article.get('title', 'No Title')
                url = article.get('url', '#')
                st.markdown(f"### [{title}]({url})")
                st.caption(f"📅 {article.get('published_date', 'Unknown')}")
                
                # Snippet removed per requirements
            
            st.markdown("---")
    
    # Update session state
    st.session_state.selected_article_ids = st.session_state.selected_article_ids
    
    return st.session_state.selected_article_ids

def preview_article(article: Dict):
    """
    Preview article content
    
    Args:
        article: Article dictionary with url, title, etc.
    """
    url = article.get('url', '')
    title = article.get('title', 'No Title')
    
    if not url:
        st.error("No URL available for preview")
        return
    
    st.write(f"**{title}**")
    st.caption(f"Source: {article.get('source', 'Unknown')} | Date: {article.get('published_date', 'Unknown')}")
    st.markdown(f"🔗 [Open Full Article]({url})")
    
    # Show loading state
    with st.spinner("Loading article content..."):
        content = get_article_content(url)
    
    if content:
        st.markdown("### Article Content Preview")
        st.text_area(
            "Content",
            value=content,
            height=300,
            disabled=True,
            key=f"preview_content_{article.get('article_id', '')}"
        )
    else:
        st.warning("Could not fetch article content. Please use the 'Open Article' link to view it.")
    
    # Show snippet if available
    snippet = article.get('snippet', '')
    if snippet:
        st.markdown("### Summary")
        st.write(snippet)

def filter_articles(articles: List[Dict], search_query: str = "", 
                   source_filter: str = "All", method_filter: str = "All") -> List[Dict]:
    """
    Filter articles by search query, source, or method
    
    Args:
        articles: List of article dictionaries
        search_query: Text to search in title/snippet
        source_filter: Source to filter by
        method_filter: Method to filter by (google/rss)
    
    Returns:
        Filtered list of articles
    """
    filtered = articles
    
    # Search query filter
    if search_query:
        query_lower = search_query.lower()
        filtered = [
            a for a in filtered
            if query_lower in a.get('title', '').lower() or
               query_lower in a.get('snippet', '').lower()
        ]
    
    # Source filter
    if source_filter != "All":
        filtered = [a for a in filtered if a.get('source') == source_filter]
    
    # Method filter
    if method_filter != "All":
        method_lower = method_filter.lower()
        filtered = [a for a in filtered if a.get('found_via', '').lower() == method_lower]
    
    return filtered

def select_articles(article_ids: List[str], articles: List[Dict]) -> List[Dict]:
    """
    Get selected articles from article list
    
    Args:
        article_ids: List of selected article IDs
        articles: Full list of articles
    
    Returns:
        List of selected article dictionaries
    """
    article_dict = {a.get('article_id'): a for a in articles}
    selected = [article_dict.get(aid) for aid in article_ids if aid in article_dict]
    return [a for a in selected if a is not None]

def show_selected_summary(selected_article_ids: set, articles: List[Dict]) -> List[Dict]:
    """
    Show summary of selected articles
    
    Args:
        selected_article_ids: Set of selected article IDs
        articles: Full list of articles
    
    Returns:
        List of selected article dictionaries
    """
    selected = select_articles(list(selected_article_ids), articles)
    
    if not selected:
        return []
    
    st.sidebar.markdown("### 📋 Selected Articles")
    st.sidebar.write(f"**{len(selected)} articles selected**")
    
    # Show selected articles list
    for idx, article in enumerate(selected[:10], 1):  # Show first 10
        st.sidebar.markdown(f"{idx}. {article.get('title', 'No Title')[:50]}...")
    
    if len(selected) > 10:
        st.sidebar.caption(f"... and {len(selected) - 10} more")
    
    return selected

def get_selected_articles_count() -> int:
    """Get count of currently selected articles"""
    return len(st.session_state.get('selected_article_ids', set()))

