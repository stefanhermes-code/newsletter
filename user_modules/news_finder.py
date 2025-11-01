"""
News Finder Module

Finds news articles using Google News search and RSS feeds.
Primary method: Google News
Secondary method: RSS feeds
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import feedparser
import logging
import time
import hashlib
import re

logger = logging.getLogger(__name__)

def find_news_google(keywords: List[str], time_period: str = "Last 7 days", max_results: int = 50) -> List[Dict]:
    """
    Find news articles using Google News search
    
    Args:
        keywords: List of keywords to search for
        time_period: Time period ("Last 7 days", "Last 14 days", "Last 30 days")
        max_results: Maximum number of results to return
    
    Returns:
        List of article dictionaries:
        [
            {
                "title": "...",
                "url": "...",
                "source": "...",
                "published_date": "...",
                "snippet": "...",
                "category": "keyword_match",
                "found_via": "google"
            },
            ...
        ]
    """
    if not keywords:
        return []
    
    articles = []
    seen_urls = set()  # For duplicate detection
    
    # Calculate date range based on time_period
    if "7" in time_period:
        days = 7
    elif "14" in time_period:
        days = 14
    elif "30" in time_period:
        days = 30
    else:
        days = 7
    
    # Build search query from keywords
    search_query = " OR ".join(keywords)
    
    # Google News search URL
    # Using Google News RSS feed approach (more reliable than scraping)
    base_url = "https://news.google.com/rss/search"
    
    # Search each keyword separately to get better coverage
    for keyword in keywords:
        try:
            # Google News RSS URL
            params = {
                "q": keyword,
                "hl": "en",
                "gl": "US",
                "ceid": "US:en"
            }
            
            # Build URL
            url = f"{base_url}?q={keyword.replace(' ', '+')}&hl=en&gl=US&ceid=US:en"
            
            # Make request
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            # Process entries
            for entry in feed.entries[:max_results // len(keywords)]:
                article_url = entry.get("link", "")
                
                # Skip duplicates
                if article_url in seen_urls:
                    continue
                
                # Extract published date
                published_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "published"):
                    try:
                        published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                    except:
                        published_date = datetime.now()
                else:
                    published_date = datetime.now()
                
                # Check if within time period
                if (datetime.now() - published_date).days > days:
                    continue
                
                # Extract source
                source = entry.get("source", {}).get("title", "Unknown")
                if not source or source == "Unknown":
                    # Try to extract from link or title
                    source = "News Source"
                
                articles.append({
                    "title": entry.get("title", ""),
                    "url": article_url,
                    "source": source,
                    "published_date": published_date.strftime("%Y-%m-%d"),
                    "published_datetime": published_date.isoformat(),
                    "snippet": entry.get("summary", ""),
                    "category": keyword,
                    "found_via": "google",
                    "article_id": hashlib.md5(article_url.encode()).hexdigest()[:12]
                })
                
                seen_urls.add(article_url)
            
            # Rate limiting
            time.sleep(0.5)
        
        except Exception as e:
            logger.error(f"Error searching Google News for keyword '{keyword}': {e}")
            continue
    
    # Sort by published date (newest first)
    articles.sort(key=lambda x: x.get("published_datetime", ""), reverse=True)
    
    return articles[:max_results]

def find_news_rss(feed_urls: List[str], time_period: str = "Last 7 days") -> List[Dict]:
    """
    Find news articles from RSS feeds (secondary method)
    
    Args:
        feed_urls: List of RSS feed URLs
        time_period: Time period ("Last 7 days", "Last 14 days", "Last 30 days")
    
    Returns:
        List of article dictionaries (same format as find_news_google)
    """
    if not feed_urls:
        return []
    
    articles = []
    seen_urls = set()
    
    # Calculate date range
    if "7" in time_period:
        days = 7
    elif "14" in time_period:
        days = 14
    elif "30" in time_period:
        days = 30
    else:
        days = 7
    
    for feed_url in feed_urls:
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing issue for {feed_url}: {feed.bozo_exception}")
            
            # Process entries
            for entry in feed.entries:
                article_url = entry.get("link", "")
                
                # Skip duplicates
                if article_url in seen_urls:
                    continue
                
                # Extract published date
                published_date = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, "published"):
                    try:
                        published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %Z")
                    except:
                        try:
                            published_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%S")
                        except:
                            published_date = datetime.now()
                else:
                    published_date = datetime.now()
                
                # Check if within time period
                if (datetime.now() - published_date).days > days:
                    continue
                
                # Extract source
                source = feed.feed.get("title", "RSS Feed")
                
                articles.append({
                    "title": entry.get("title", ""),
                    "url": article_url,
                    "source": source,
                    "published_date": published_date.strftime("%Y-%m-%d"),
                    "published_datetime": published_date.isoformat(),
                    "snippet": entry.get("summary", ""),
                    "category": source,  # Use feed name as category
                    "found_via": "rss",
                    "article_id": hashlib.md5(article_url.encode()).hexdigest()[:12]
                })
                
                seen_urls.add(article_url)
        
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            continue
    
    # Sort by published date (newest first)
    articles.sort(key=lambda x: x.get("published_datetime", ""), reverse=True)
    
    return articles

def find_news_background(keywords: List[str], feed_urls: List[str], time_period: str = "Last 7 days", 
                         progress_callback: Optional[callable] = None) -> List[Dict]:
    """
    Combined news finding (Google primary, RSS secondary)
    Runs in background with progress updates
    
    Args:
        keywords: List of keywords for Google News
        feed_urls: List of RSS feed URLs
        time_period: Time period string
        progress_callback: Optional callback function(status_message) for progress updates
    
    Returns:
        Combined and deduplicated list of articles
    """
    all_articles = []
    seen_urls = set()
    
    # Step 1: Google News (primary)
    if keywords:
        if progress_callback:
            progress_callback("🔍 Searching Google News...")
        
        google_articles = find_news_google(keywords, time_period)
        all_articles.extend(google_articles)
        seen_urls.update(a["url"] for a in google_articles)
    
    # Step 2: RSS Feeds (secondary)
    if feed_urls:
        if progress_callback:
            progress_callback("📡 Checking RSS feeds...")
        
        rss_articles = find_news_rss(feed_urls, time_period)
        
        # Only add RSS articles not found via Google
        for article in rss_articles:
            if article["url"] not in seen_urls:
                all_articles.append(article)
                seen_urls.add(article["url"])
    
    # Remove exact duplicates (same URL)
    unique_articles = []
    seen = set()
    for article in all_articles:
        if article["url"] not in seen:
            unique_articles.append(article)
            seen.add(article["url"])
    
    # Sort by published date (newest first)
    unique_articles.sort(key=lambda x: x.get("published_datetime", ""), reverse=True)
    
    if progress_callback:
        progress_callback(f"✅ Found {len(unique_articles)} articles")
    
    return unique_articles

def categorize_articles(articles: List[Dict], keywords: List[str]) -> Dict[str, List[Dict]]:
    """
    Categorize articles based on keywords (for organization)
    
    Args:
        articles: List of article dictionaries
        keywords: List of keywords
    
    Returns:
        Dictionary mapping categories to article lists
    """
    categorized = {}
    
    for keyword in keywords:
        categorized[keyword] = []
    
    # Add "Other" category
    categorized["Other"] = []
    
    for article in articles:
        title_lower = article.get("title", "").lower()
        snippet_lower = article.get("snippet", "").lower()
        
        # Find matching keyword
        matched = False
        for keyword in keywords:
            if keyword.lower() in title_lower or keyword.lower() in snippet_lower:
                categorized[keyword].append(article)
                matched = True
                break
        
        if not matched:
            categorized["Other"].append(article)
    
    return categorized

def get_article_content(url: str) -> Optional[str]:
    """
    Fetch and extract text content from article URL (for preview)
    
    Args:
        url: Article URL
    
    Returns:
        Extracted text content, or None if error
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit length (first 2000 characters for preview)
        if len(text) > 2000:
            text = text[:2000] + "..."
        
        return text
    
    except Exception as e:
        logger.error(f"Error fetching article content from {url}: {e}")
        return None

