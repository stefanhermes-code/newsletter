"""
Category mapping for newsletter section grouping.
"""

from __future__ import annotations

from collections import OrderedDict
from typing import Dict, List, Optional, Tuple

DEFAULT_CATEGORIES = [
    "Materials & Chemistry",
    "Sustainability & Recycling",
    "Regulations & Safety",
    "Markets & Industry",
    "Applications",
    "Supply Chain Disruptions",
    "Other",
]


def load_category_config(customer_id: str) -> Dict:
    """Load categories.json for a customer; return defaults if missing."""
    # Prefer local file (works before GitHub sync / offline)
    try:
        from pathlib import Path
        import json

        local_path = Path(f"customers/{customer_id}/config/categories.json")
        if local_path.exists():
            with open(local_path, encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass

    try:
        from user_modules.github_user import load_config

        config = load_config(customer_id, "categories")
        if config:
            return config
    except Exception:
        pass
    return {
        "categories": DEFAULT_CATEGORIES,
        "keyword_mappings": {},
    }


def resolve_section(keyword_or_category: str, mappings: Dict[str, str], categories: List[str]) -> str:
    """Map a matched keyword/feed name to a newsletter section."""
    if not keyword_or_category:
        return "Other"

    # Exact mapping
    if keyword_or_category in mappings:
        return mappings[keyword_or_category]

    # Case-insensitive exact
    lower_map = {k.lower(): v for k, v in mappings.items()}
    key_l = keyword_or_category.lower()
    if key_l in lower_map:
        return lower_map[key_l]

    # If the value is already a known section name
    if keyword_or_category in categories:
        return keyword_or_category

    return "Other"


def assign_sections(articles: List[Dict], category_config: Dict) -> List[Dict]:
    """Return article copies with newsletter_section set."""
    mappings = category_config.get("keyword_mappings") or {}
    categories = category_config.get("categories") or DEFAULT_CATEGORIES
    result = []
    for article in articles:
        item = dict(article)
        raw = item.get("category") or item.get("matched_keyword") or ""
        item["newsletter_section"] = resolve_section(raw, mappings, categories)
        result.append(item)
    return result


def group_by_section(
    articles: List[Dict],
    category_config: Optional[Dict] = None,
) -> OrderedDict:
    """
    Group articles by newsletter_section, preserving configured category order.
    """
    config = category_config or {"categories": DEFAULT_CATEGORIES}
    categories = list(config.get("categories") or DEFAULT_CATEGORIES)
    if "Other" not in categories:
        categories.append("Other")

    # Ensure sections assigned
    if articles and "newsletter_section" not in articles[0]:
        articles = assign_sections(articles, config)

    grouped: OrderedDict[str, List[Dict]] = OrderedDict((c, []) for c in categories)
    for article in articles:
        section = article.get("newsletter_section") or "Other"
        if section not in grouped:
            grouped[section] = []
        grouped[section].append(article)

    # Drop empty sections
    return OrderedDict((k, v) for k, v in grouped.items() if v)


def draft_intro_from_articles(articles: List[Dict], category_config: Optional[Dict] = None) -> str:
    """
    Draft a short 3–4 sentence intro from selected articles (editable by user).
    """
    if not articles:
        return ""

    config = category_config or {"categories": DEFAULT_CATEGORIES}
    assigned = assign_sections(articles, config)
    grouped = group_by_section(assigned, config)

    count = len(assigned)
    section_names = list(grouped.keys())
    if len(section_names) == 1:
        sections_phrase = section_names[0]
    elif len(section_names) == 2:
        sections_phrase = f"{section_names[0]} and {section_names[1]}"
    else:
        sections_phrase = ", ".join(section_names[:-1]) + f", and {section_names[-1]}"

    highlights = []
    for art in assigned[:3]:
        title = (art.get("title") or "").strip()
        if title:
            # Keep titles readable in a sentence
            if len(title) > 90:
                title = title[:87] + "…"
            highlights.append(title)

    sentences = [
        f"This week's newsletter brings together {count} selected stories across {sections_phrase}.",
    ]
    if highlights:
        if len(highlights) == 1:
            sentences.append(f"Among the highlights is: {highlights[0]}.")
        else:
            joined = "; ".join(highlights)
            sentences.append(f"Key items include: {joined}.")
    sentences.append(
        "Browse the sections below for the full set of links and publication dates."
    )
    if "Supply Chain Disruptions" in section_names:
        sentences.append(
            "Pay particular attention to Supply Chain Disruptions for developments that may affect availability and pricing."
        )
    return " ".join(sentences[:4])


def suggest_banner_theme(articles: List[Dict], category_config: Optional[Dict] = None) -> str:
    """Pick a short theme label for banner overlay (largest section)."""
    if not articles:
        return "Industry Pulse"
    config = category_config or {"categories": DEFAULT_CATEGORIES}
    grouped = group_by_section(assign_sections(articles, config), config)
    if not grouped:
        return "Industry Pulse"
    top = max(grouped.items(), key=lambda kv: len(kv[1]))
    return top[0]


def keywords_for_categories(
    selected_categories: List[str],
    all_keywords: List[str],
    category_config: Dict,
) -> List[str]:
    """Return keywords whose mapped section is in selected_categories."""
    if not selected_categories:
        return []
    mappings = category_config.get("keyword_mappings") or {}
    categories = category_config.get("categories") or DEFAULT_CATEGORIES
    selected = set(selected_categories)
    matched = []
    for kw in all_keywords:
        if not kw:
            continue
        section = resolve_section(kw, mappings, categories)
        if section in selected:
            matched.append(kw)
    return matched


def merge_search_keywords(
    selected_categories: List[str],
    selected_keywords: List[str],
    all_keywords: List[str],
    category_config: Dict,
) -> List[str]:
    """
    Union of keywords from selected categories and individually selected keywords.
    Preserves order: category-expanded first, then extra individual picks.
    """
    from_cats = keywords_for_categories(selected_categories, all_keywords, category_config)
    seen = set()
    merged = []
    for kw in from_cats + list(selected_keywords or []):
        if kw and kw not in seen:
            seen.add(kw)
            merged.append(kw)
    return merged


def available_search_categories(category_config: Dict, all_keywords: List[str]) -> List[str]:
    """Categories that have at least one mapped keyword (exclude empty Other unless used)."""
    categories = list(category_config.get("categories") or DEFAULT_CATEGORIES)
    mappings = category_config.get("keyword_mappings") or {}
    used = set()
    for kw in all_keywords:
        used.add(resolve_section(kw, mappings, categories))
    return [c for c in categories if c in used and c != "Other"] + (
        ["Other"] if "Other" in used else []
    )
