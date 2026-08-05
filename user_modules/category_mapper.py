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


# Theme cues used when the exact keyword is not present in the title
_SECTION_CUES = [
    (
        "Supply Chain Disruptions",
        (
            "tariff", "tariffs", "anti-dumping", "antidumping", "hormuz",
            "supply chain", "freight", "shipping", "sanction", "blockade",
            "port", "logistics", "raw material volatility", "trade war",
            "export ban", "import duty", "duties",
        ),
    ),
    (
        "Sustainability & Recycling",
        (
            "recycl", "circular", "bio-based", "biobased", "biopolyol", "repolyol",
            "sustainab", "carbon", "net-zero", "net zero", "life cycle", "lca",
            "low-voc", "low emission", "waste", "rebond", "glycolysis",
            "hydrolysis", "aminolysis",
        ),
    ),
    (
        "Regulations & Safety",
        (
            "reach", "regulation", "compliance", "restriction", "worker safety",
            "health and safety", "flame retard", "fire retard", "isocyanate restriction",
        ),
    ),
    (
        "Markets & Industry",
        (
            "acquisition", "merger", "divest", "joint venture", "capacity",
            "investment", "pricing", "market growth", "demand", "plant restart",
            "debottleneck", "ipo", "takeover", "earnings", "stock",
        ),
    ),
    (
        "Applications",
        (
            "automotive", "mattress", "furniture", "insulation", "footwear",
            "construction", "3d print", "bedding", "seating", "spray foam",
            "cold chain", "appliance", "nvh",
        ),
    ),
    (
        "Materials & Chemistry",
        (
            "polyol", "isocyanate", "catalyst", "elastomer", "foam", "coating",
            "adhesive", "sealant", "prepolymer", "surfactant", "blowing agent",
            "tpu", "case ", "rim ", "polyurethane", "pu ",
        ),
    ),
]


def _normalize_match_text(text: str) -> str:
    return " ".join((text or "").lower().replace("-", " ").split())


def match_keyword_in_text(text: str, keywords: List[str]) -> str:
    """
    Return best keyword match for text (title), or ''.

    Tries longest exact phrase first, then looser token/stem matches
    (e.g. 'Tariffs' ↔ 'tariff', 'Strait of Hormuz' ↔ 'Hormuz').
    """
    hay = _normalize_match_text(text)
    if not hay or not keywords:
        return ""

    keywords_sorted = sorted([k for k in keywords if k], key=len, reverse=True)

    # 1) Exact phrase
    for kw in keywords_sorted:
        if _normalize_match_text(kw) in hay:
            return kw

    # 2) Significant tokens (ignore short glue words)
    stop = {"of", "the", "and", "in", "for", "a", "an", "to", "on", "or"}
    for kw in keywords_sorted:
        tokens = [t for t in _normalize_match_text(kw).split() if t not in stop and len(t) >= 4]
        if not tokens:
            continue
        # All significant tokens present, or the distinctive last token for multi-word kws
        if all(t in hay for t in tokens):
            return kw
        if len(tokens) >= 2 and tokens[-1] in hay and len(tokens[-1]) >= 5:
            return kw

    # 3) Simple plural/stem: keyword without trailing s
    for kw in keywords_sorted:
        stem = _normalize_match_text(kw).rstrip("s")
        if len(stem) >= 5 and stem in hay:
            return kw

    return ""


def section_from_cues(text: str, categories: List[str]) -> str:
    """Fallback section from thematic cues in title/snippet."""
    hay = _normalize_match_text(text)
    if not hay:
        return "Other"
    allowed = set(categories or DEFAULT_CATEGORIES)
    for section, cues in _SECTION_CUES:
        if section not in allowed and section != "Other":
            continue
        if any(c in hay for c in cues):
            return section
    return "Other"


def classify_article_section(
    article: Dict,
    all_keywords: List[str],
    category_config: Dict,
) -> str:
    """
    Best-effort section for an article using:
    1) stored matched keyword / category field
    2) keyword match against title (+ snippet)
    3) thematic cues
    """
    mappings = category_config.get("keyword_mappings") or {}
    categories = category_config.get("categories") or DEFAULT_CATEGORIES

    raw = (article.get("category") or article.get("matched_keyword") or "").strip()
    if raw:
        section = resolve_section(raw, mappings, categories)
        if section != "Other":
            return section

    if article.get("newsletter_section") in categories:
        return article["newsletter_section"]

    blob = f"{article.get('title') or ''} {article.get('snippet') or ''}"
    kw = match_keyword_in_text(blob, all_keywords or list(mappings.keys()))
    if kw:
        return resolve_section(kw, mappings, categories)

    return section_from_cues(blob, categories)


def assign_sections(articles: List[Dict], category_config: Dict) -> List[Dict]:
    """Return article copies with newsletter_section set."""
    mappings = category_config.get("keyword_mappings") or {}
    all_keywords = list(mappings.keys())
    result = []
    for article in articles:
        item = dict(article)
        item["newsletter_section"] = classify_article_section(
            item, all_keywords, category_config
        )
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


def draft_intro_from_articles(
    articles: List[Dict],
    category_config: Optional[Dict] = None,
    newsletter_name: str = "",
) -> str:
    """
    Draft a short editorial intro (3–4 sentences).

    Summarises themes in context — no article counts, no title lists.
    Uses the customer newsletter name (e.g. APBA NewsBulletin), not banner taglines.
    """
    if not articles:
        return ""

    name = (newsletter_name or "").strip() or "This week's newsletter"
    # "This week's APBA NewsBulletin …" vs already including "newsletter"
    if name.lower().startswith("this week's"):
        week_label = name
    else:
        week_label = f"This week's {name}"

    config = category_config or {"categories": DEFAULT_CATEGORIES}
    assigned = assign_sections(articles, config)
    grouped = group_by_section(assigned, config)
    sections = list(grouped.keys())

    # Theme cues from titles (not quoted back as a list)
    blob = " ".join((a.get("title") or "") for a in assigned).lower()
    cues = []
    cue_map = [
        (("tariff", "anti-dumping", "hormuz", "supply chain", "freight", "shipping", "sanctions"),
         "trade friction and supply-chain pressure"),
        (("recycl", "circular", "bio-based", "biopolyol", "repolyol", "sustainab", "carbon", "net-zero"),
         "circularity and lower-carbon materials"),
        (("reach", "regulation", "compliance", "isocyanate restriction", "safety", "flame retard"),
         "regulatory and safety developments"),
        (("price", "capacity", "investment", "merger", "acquisition", "market", "demand"),
         "market and investment signals"),
        (("automotive", "mattress", "furniture", "insulation", "footwear", "construction", "3d print"),
         "downstream application trends"),
        (("polyol", "isocyanate", "catalyst", "elastomer", "foam", "coating", "adhesive"),
         "materials and chemistry advances"),
    ]
    for keys, label in cue_map:
        if any(k in blob for k in keys):
            cues.append(label)
    cues = cues[:3]

    focus_sections = [s for s in sections if s != "Other"]
    if not focus_sections:
        focus_sections = sections

    if len(focus_sections) == 1:
        openers = (
            f"{week_label} centres on {focus_sections[0].lower()}, "
            f"and what those developments mean for polyurethane businesses across Asia."
        )
    elif len(focus_sections) == 2:
        openers = (
            f"{week_label} connects {focus_sections[0].lower()} with "
            f"{focus_sections[1].lower()}, tracing how both are shaping decisions in the value chain."
        )
    else:
        openers = (
            f"{week_label} steps across the polyurethane landscape — "
            "from upstream chemistry and trade conditions to how converters and end-markets are responding."
        )

    if cues:
        if len(cues) == 1:
            mid = f"The through-line is {cues[0]}."
        elif len(cues) == 2:
            mid = f"Watch especially for {cues[0]}, alongside {cues[1]}."
        else:
            mid = f"Watch especially for {cues[0]}, {cues[1]}, and {cues[2]}."
    else:
        mid = (
            "Rather than a round-up of headlines, the aim is to frame the week so "
            "members can see where risk and opportunity are concentrating."
        )

    if "Supply Chain Disruptions" in sections:
        close = (
            "Supply-chain items are grouped so you can judge exposure quickly; "
            "the remaining sections organise the rest by theme."
        )
    elif "Regulations & Safety" in sections:
        close = (
            "Compliance-sensitive items are kept together so operational and "
            "commercial teams can scan what may affect market access."
        )
    else:
        close = (
            "Use the sections below to move straight to the themes most relevant "
            "to your products, customers, and geography."
        )

    return " ".join([openers, mid, close])


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
