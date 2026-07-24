"""
Short.io client for newsletter link tracking.

Creates branded short links with UTMs and optional expiry/cleanup.
Requires Streamlit secrets: shortio_api_key, shortio_domain.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

import requests
import streamlit as st

logger = logging.getLogger(__name__)

API_BASE = "https://api.short.io"
DEFAULT_TTL_DAYS = 60


def _get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Return (api_key, domain) from Streamlit secrets, or (None, None)."""
    try:
        if not hasattr(st, "secrets") or not st.secrets:
            return None, None
        api_key = st.secrets.get("shortio_api_key")
        domain = st.secrets.get("shortio_domain")
        if not api_key or not domain:
            return None, None
        return str(api_key), str(domain)
    except Exception as e:
        logger.warning(f"Short.io secrets unavailable: {e}")
        return None, None


def is_configured() -> bool:
    api_key, domain = _get_credentials()
    return bool(api_key and domain)


def create_short_link(
    original_url: str,
    *,
    title: str = "",
    campaign: str = "",
    tags: Optional[List[str]] = None,
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> Optional[Dict]:
    """
    Create a short link. Returns Short.io link dict on success, else None.
    """
    api_key, domain = _get_credentials()
    if not api_key or not domain:
        return None

    # Note: expiresAt requires Short.io Pro — Free plan uses cleanup_old_links() instead
    payload = {
        "originalURL": original_url,
        "domain": domain,
        "allowDuplicates": True,
        "utmSource": "linkedin",
        "utmMedium": "newsletter",
    }
    if campaign:
        payload["utmCampaign"] = campaign
    if title:
        payload["title"] = title[:200]
    if tags:
        payload["tags"] = tags

    try:
        resp = requests.post(
            f"{API_BASE}/links",
            headers={
                "Authorization": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=20,
        )
        if resp.status_code >= 400:
            logger.error(f"Short.io create failed ({resp.status_code}): {resp.text}")
            return None
        return resp.json()
    except Exception as e:
        logger.error(f"Short.io create error: {e}")
        return None


def shorten_articles(
    articles: List[Dict],
    *,
    campaign: str,
    tag_prefix: str = "newsletter",
    ttl_days: int = DEFAULT_TTL_DAYS,
) -> Tuple[List[Dict], int, int]:
    """
    Return articles with url replaced by short links when possible.

    Returns: (articles_copy, shortened_count, failed_count)
    """
    if not is_configured():
        return articles, 0, 0

    result = []
    ok = 0
    failed = 0
    week_tag = campaign or "newsletter"

    for article in articles:
        item = dict(article)
        original = item.get("url") or ""
        if not original or original == "#":
            result.append(item)
            continue

        link = create_short_link(
            original,
            title=item.get("title", ""),
            campaign=week_tag,
            tags=[tag_prefix, week_tag],
            ttl_days=ttl_days,
        )
        if link and link.get("shortURL"):
            item["original_url"] = original
            item["url"] = link["shortURL"]
            item["shortio_id"] = link.get("id") or link.get("idString")
            ok += 1
        else:
            failed += 1
        result.append(item)

    return result, ok, failed


def delete_link(link_id) -> bool:
    """Delete a Short.io link by id."""
    api_key, _ = _get_credentials()
    if not api_key or link_id is None:
        return False
    try:
        resp = requests.delete(
            f"{API_BASE}/links/{link_id}",
            headers={"Authorization": api_key, "Accept": "application/json"},
            timeout=20,
        )
        return resp.status_code < 400
    except Exception as e:
        logger.error(f"Short.io delete error: {e}")
        return False


def cleanup_old_links(older_than_days: int = DEFAULT_TTL_DAYS, limit: int = 100) -> int:
    """
    Delete links older than older_than_days on the configured domain.
    Returns number deleted. Best-effort; failures are logged.
    """
    api_key, domain = _get_credentials()
    if not api_key or not domain:
        return 0

    try:
        # Resolve domain id
        domains_resp = requests.get(
            f"{API_BASE}/api/domains",
            headers={"Authorization": api_key, "Accept": "application/json"},
            timeout=20,
        )
        domains_resp.raise_for_status()
        domains = domains_resp.json()
        if isinstance(domains, dict):
            domains = domains.get("value") or domains.get("domains") or []
        domain_id = None
        for d in domains:
            if d.get("hostname") == domain or d.get("unicodeHostname") == domain:
                domain_id = d.get("id")
                break
        if not domain_id:
            logger.warning(f"Short.io domain not found: {domain}")
            return 0

        links_resp = requests.get(
            f"{API_BASE}/api/links",
            headers={"Authorization": api_key, "Accept": "application/json"},
            params={"domain_id": domain_id, "limit": limit, "page": 0},
            timeout=30,
        )
        links_resp.raise_for_status()
        data = links_resp.json()
        links = data if isinstance(data, list) else data.get("links") or data.get("items") or []

        cutoff = datetime.now(timezone.utc) - timedelta(days=older_than_days)
        deleted = 0
        for link in links:
            created = link.get("createdAt")
            if not created:
                continue
            try:
                if isinstance(created, (int, float)):
                    created_dt = datetime.fromtimestamp(created / 1000.0, tz=timezone.utc)
                else:
                    created_dt = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            except Exception:
                continue
            if created_dt < cutoff:
                lid = link.get("id") or link.get("idString")
                if lid and delete_link(lid):
                    deleted += 1
        return deleted
    except Exception as e:
        logger.error(f"Short.io cleanup error: {e}")
        return 0
