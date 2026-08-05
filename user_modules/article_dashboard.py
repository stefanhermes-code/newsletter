"""
Article Dashboard Module

Displays articles, provides preview functionality, and handles article selection
for newsletter generation.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Set

import streamlit as st

from user_modules.news_finder import get_article_content

logger = logging.getLogger(__name__)


def _ensure_selection_state() -> Set[str]:
    if "selected_article_ids" not in st.session_state:
        st.session_state.selected_article_ids = set()
    if not isinstance(st.session_state.selected_article_ids, set):
        st.session_state.selected_article_ids = set(st.session_state.selected_article_ids)
    if "article_bank" not in st.session_state:
        st.session_state.article_bank = {}
    return st.session_state.selected_article_ids


def merge_into_article_bank(articles: List[Dict]) -> None:
    """Accumulate articles by id so selections survive new searches / filters."""
    _ensure_selection_state()
    bank: Dict[str, Dict] = st.session_state.article_bank
    for article in articles or []:
        aid = article.get("article_id")
        if aid:
            bank[aid] = article
    st.session_state.article_bank = bank


def merge_found_articles(existing: List[Dict], new_articles: List[Dict]) -> List[Dict]:
    """Union articles by article_id (new values win). Preserves prior results."""
    merged: Dict[str, Dict] = {}
    for article in (existing or []) + (new_articles or []):
        aid = article.get("article_id")
        if not aid:
            continue
        merged[aid] = article
    merge_into_article_bank(list(merged.values()))
    return list(merged.values())


def lookup_articles(article_ids, articles: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Resolve selected ids to article dicts.
    Prefers article_bank, then the provided list (usually found_articles).
    """
    _ensure_selection_state()
    bank: Dict[str, Dict] = dict(st.session_state.article_bank)
    for article in articles or []:
        aid = article.get("article_id")
        if aid:
            bank[aid] = article

    selected = []
    for aid in article_ids or []:
        if aid in bank:
            selected.append(bank[aid])
    return selected


def _parse_article_date(article: Dict) -> Optional[date]:
    dt_iso = article.get("published_datetime", "")
    if dt_iso:
        try:
            return datetime.fromisoformat(dt_iso).date()
        except Exception:
            pass
    d_plain = article.get("published_date", "")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(d_plain, fmt).date()
        except Exception:
            continue
    return None


def display_articles(articles: List[Dict], selected_article_ids: Optional[set] = None) -> set:
    """
    Display articles with category + keyword + date filters and durable selection.
    Changing filters only changes what is visible — selections are kept.
    """
    selected_ids = _ensure_selection_state()
    if selected_article_ids:
        selected_ids |= set(selected_article_ids)
        st.session_state.selected_article_ids = selected_ids

    merge_into_article_bank(articles)

    if not articles:
        st.info("No articles found. Try adjusting your search criteria.")
        return st.session_state.selected_article_ids

    # Enrich with newsletter section for filtering
    from user_modules.category_mapper import (
        assign_sections,
        load_category_config,
    )

    customer_id = st.session_state.get("current_customer_id") or ""
    category_config = load_category_config(customer_id) if customer_id else {
        "categories": [],
        "keyword_mappings": {},
    }
    enriched = assign_sections(articles, category_config)

    st.write(f"**Found {len(enriched)} articles** in current results")
    st.caption(
        f"**{len(st.session_state.selected_article_ids)}** selected in total "
        "(selection is kept when you change filters or add another search)."
    )

    col_cat, col_kw, col_from, col_to = st.columns([3, 3, 2, 2])

    section_options = []
    for a in enriched:
        sec = (a.get("newsletter_section") or "").strip()
        if sec and sec not in section_options:
            section_options.append(sec)
    # Keep configured order when possible
    configured = category_config.get("categories") or []
    section_options = [c for c in configured if c in section_options] + [
        c for c in section_options if c not in configured
    ]

    with col_cat:
        selected_sections = st.multiselect(
            "Category",
            options=section_options,
            default=[],
            key="article_filter_categories",
            help="Filter the list by newsletter category. Selection is not cleared when you change this.",
        )

    # Keyword options: optionally narrowed to selected categories
    keyword_pool = enriched
    if selected_sections:
        keyword_pool = [
            a for a in enriched
            if (a.get("newsletter_section") or "") in selected_sections
        ]
    keyword_options = sorted(
        {a.get("category", "").strip() for a in keyword_pool if a.get("category")}
    )

    with col_kw:
        selected_keywords = st.multiselect(
            "Keyword(s)",
            options=keyword_options,
            default=[],
            key="article_filter_keywords_multi",
            help="Optional: narrow further by the matched search keyword.",
        )

    dates = [d for d in (_parse_article_date(a) for a in enriched) if d]
    min_date = min(dates) if dates else date.today()
    max_date = max(dates) if dates else date.today()

    with col_from:
        start_date = st.date_input("From", value=min_date, key="filter_from_date")
    with col_to:
        end_date = st.date_input("To", value=max_date, key="filter_to_date")

    filtered_articles = enriched
    if selected_sections:
        filtered_articles = [
            a for a in filtered_articles
            if (a.get("newsletter_section") or "") in selected_sections
        ]
    if selected_keywords:
        selected_set = {k.lower() for k in selected_keywords}
        filtered_articles = [
            a for a in filtered_articles
            if a.get("category") and a.get("category").lower() in selected_set
        ]
    if start_date and end_date:
        def in_range(a: Dict) -> bool:
            d = _parse_article_date(a)
            if d is None:
                return True
            return start_date <= d <= end_date

        filtered_articles = [a for a in filtered_articles if in_range(a)]

    st.write(f"**Showing {len(filtered_articles)} articles** (filtered view)")

    btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 2, 6])
    with btn_col1:
        if st.button("Select visible", key="select_all_articles"):
            for article in filtered_articles:
                aid = article.get("article_id", "")
                if aid:
                    st.session_state.selected_article_ids.add(aid)
                    st.session_state[f"article_checkbox_{aid}"] = True
            st.rerun()
    with btn_col2:
        if st.button("Clear selection", key="clear_selection"):
            for aid in list(st.session_state.selected_article_ids):
                st.session_state[f"article_checkbox_{aid}"] = False
            st.session_state.selected_article_ids = set()
            st.rerun()
    with btn_col3:
        if st.button("Clear results list", key="clear_found_articles"):
            st.session_state.found_articles = []
            # Keep bank + selection so Generate still works for already chosen items
            st.rerun()

    st.markdown("---")

    for idx, article in enumerate(filtered_articles):
        article_id = article.get("article_id") or f"missing_{idx}"
        is_selected = article_id in st.session_state.selected_article_ids

        with st.container():
            col1, col2 = st.columns([1, 10])

            with col1:
                checkbox_key = f"article_checkbox_{article_id}"
                # Initialise from durable selection; do not reset on every filter change
                if checkbox_key not in st.session_state:
                    st.session_state[checkbox_key] = is_selected

                selected = st.checkbox("", key=checkbox_key)

                currently_selected = article_id in st.session_state.selected_article_ids
                if selected and not currently_selected:
                    st.session_state.selected_article_ids.add(article_id)
                    st.rerun()
                elif not selected and currently_selected:
                    st.session_state.selected_article_ids.discard(article_id)
                    st.rerun()

            with col2:
                title = article.get("title", "No Title")
                url = article.get("url", "#")
                section = article.get("newsletter_section") or "Other"
                keyword = article.get("category") or ""
                st.markdown(f"### [{title}]({url})")
                meta = f"📅 {article.get('published_date', 'Unknown')} · {section}"
                if keyword and keyword != section:
                    meta += f" · ⌕ {keyword}"
                st.caption(meta)

            st.markdown("---")

    return st.session_state.selected_article_ids


def preview_article(article: Dict):
    """Preview article content."""
    url = article.get("url", "")
    title = article.get("title", "No Title")

    if not url:
        st.error("No URL available for preview")
        return

    st.write(f"**{title}**")
    st.caption(
        f"Source: {article.get('source', 'Unknown')} | Date: {article.get('published_date', 'Unknown')}"
    )
    st.markdown(f"🔗 [Open Full Article]({url})")

    with st.spinner("Loading article content..."):
        content = get_article_content(url)

    if content:
        st.markdown("### Article Content Preview")
        st.text_area(
            "Content",
            value=content,
            height=300,
            disabled=True,
            key=f"preview_content_{article.get('article_id', '')}",
        )
    else:
        st.warning("Could not fetch article content. Please use the 'Open Article' link to view it.")

    snippet = article.get("snippet", "")
    if snippet:
        st.markdown("### Summary")
        st.write(snippet)


def filter_articles(
    articles: List[Dict],
    search_query: str = "",
    source_filter: str = "All",
    method_filter: str = "All",
) -> List[Dict]:
    """Filter articles by search query, source, or method."""
    filtered = articles

    if search_query:
        query_lower = search_query.lower()
        filtered = [
            a
            for a in filtered
            if query_lower in a.get("title", "").lower()
            or query_lower in a.get("snippet", "").lower()
        ]

    if source_filter != "All":
        filtered = [a for a in filtered if a.get("source") == source_filter]

    if method_filter != "All":
        method_lower = method_filter.lower()
        filtered = [
            a for a in filtered if a.get("found_via", "").lower() == method_lower
        ]

    return filtered


def select_articles(article_ids: List[str], articles: List[Dict]) -> List[Dict]:
    """Get selected articles from bank + article list."""
    return lookup_articles(article_ids, articles)


def show_selected_summary(selected_article_ids: set, articles: List[Dict]) -> List[Dict]:
    """Show summary of selected articles (from bank so hidden/filtered ones still count)."""
    selected = lookup_articles(list(selected_article_ids), articles)

    if not selected:
        return []

    st.sidebar.markdown("### 📋 Selected Articles")
    st.sidebar.write(f"**{len(selected)} articles selected**")

    for idx, article in enumerate(selected[:10], 1):
        st.sidebar.markdown(f"{idx}. {article.get('title', 'No Title')[:50]}...")

    if len(selected) > 10:
        st.sidebar.caption(f"... and {len(selected) - 10} more")

    return selected


def get_selected_articles_count() -> int:
    """Get count of currently selected articles"""
    return len(st.session_state.get("selected_article_ids", set()))
