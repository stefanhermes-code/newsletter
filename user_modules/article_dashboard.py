"""
Article Dashboard Module

Displays articles, provides preview functionality, and handles article selection
for newsletter generation.
"""

import streamlit as st
from typing import List, Dict, Optional
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
    if 'selected_article_ids' not in st.session_state:
        st.session_state.selected_article_ids = selected_article_ids.copy()
    
    st.write(f"**Found {len(articles)} articles**")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_source = st.selectbox(
            "Filter by Source",
            ["All"] + list(set(a.get("source", "Unknown") for a in articles)),
            key="article_filter_source"
        )
    
    with col2:
        filter_method = st.selectbox(
            "Filter by Method",
            ["All", "Google", "RSS"],
            key="article_filter_method"
        )
    
    with col3:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All"] + list(set(a.get("category", "Other") for a in articles)),
            key="article_filter_category"
        )
    
    # Apply filters
    filtered_articles = articles
    if filter_source != "All":
        filtered_articles = [a for a in filtered_articles if a.get("source") == filter_source]
    if filter_method != "All":
        filtered_articles = [a for a in filtered_articles if a.get("found_via", "").lower() == filter_method.lower()]
    if filter_category != "All":
        filtered_articles = [a for a in filtered_articles if a.get("category") == filter_category]
    
    st.write(f"**Showing {len(filtered_articles)} articles** (filtered)")
    
    # Selection controls
    col1, col2 = st.columns([3, 1])
    with col1:
        st.write("")
    with col2:
        if st.button("Select All", key="select_all_articles"):
            st.session_state.selected_article_ids = set(a["article_id"] for a in filtered_articles)
            st.rerun()
        if st.button("Clear Selection", key="clear_selection"):
            st.session_state.selected_article_ids = set()
            st.rerun()
    
    st.markdown("---")
    
    # Display articles
    for idx, article in enumerate(filtered_articles):
        article_id = article.get("article_id", str(idx))
        is_selected = article_id in st.session_state.selected_article_ids
        
        # Article card
        with st.container():
            col1, col2 = st.columns([1, 10])
            
            with col1:
                # Checkbox for selection
                selected = st.checkbox(
                    "",
                    value=is_selected,
                    key=f"article_checkbox_{article_id}"
                )
                
                if selected != is_selected:
                    if selected:
                        st.session_state.selected_article_ids.add(article_id)
                    else:
                        st.session_state.selected_article_ids.discard(article_id)
            
            with col2:
                # Article info
                st.markdown(f"### {article.get('title', 'No Title')}")
                
                col_info1, col_info2, col_info3 = st.columns(3)
                
                with col_info1:
                    st.caption(f"📰 **Source:** {article.get('source', 'Unknown')}")
                
                with col_info2:
                    st.caption(f"📅 **Date:** {article.get('published_date', 'Unknown')}")
                
                with col_info3:
                    method_icon = "🔍" if article.get('found_via') == 'google' else "📡"
                    st.caption(f"{method_icon} **Via:** {article.get('found_via', 'unknown').upper()}")
                
                # Snippet
                snippet = article.get('snippet', '')
                if snippet:
                    st.write(snippet[:200] + "..." if len(snippet) > 200 else snippet)
                
                # Actions
                col_action1, col_action2 = st.columns([1, 10])
                
                with col_action1:
                    # Preview button
                    preview_key = f"preview_{article_id}"
                    if st.button("👁️ Preview", key=preview_key):
                        st.session_state[f'preview_article_{article_id}'] = True
                
                with col_action2:
                    # Open link button
                    st.markdown(f"[🔗 Open Article]({article.get('url', '#')})")
                
                # Preview section (if triggered)
                if st.session_state.get(f'preview_article_{article_id}', False):
                    with st.expander("📄 Article Preview", expanded=True):
                        preview_article(article)
                        # Close preview button
                        if st.button("Close Preview", key=f"close_preview_{article_id}"):
                            st.session_state[f'preview_article_{article_id}'] = False
                            st.rerun()
            
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

