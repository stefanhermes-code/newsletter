"""
Analytics Engine Module

Cross-customer analytics and insights.
"""

import streamlit as st
from typing import List, Dict, Optional
from admin_modules.customer_manager import get_customer_details, get_customer_list
from admin_modules.github_admin import list_all_customers, list_customer_files
from collections import Counter
from datetime import datetime, timedelta

def render_analytics():
    """Render analytics dashboard"""
    st.header("Analytics")
    
    tab1, tab2 = st.tabs(["Usage Patterns", "Trend Analysis"])
    
    with tab1:
        render_usage_patterns()
    
    with tab2:
        render_trend_analysis()

def render_usage_patterns():
    """Show usage patterns across customers"""
    st.subheader("Usage Patterns")
    
    all_customers = get_customer_list()
    
    if not all_customers:
        st.info("No customers found for analytics.")
        return
    
    # Get popular keywords
    popular_keywords = get_popular_keywords()
    
    # Get popular feeds
    popular_feeds = get_popular_feeds()
    
    # Get most active customers
    active_customers = get_most_active_customers()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Top Keywords (Across All Customers):**")
        if popular_keywords:
            for idx, (keyword, count) in enumerate(popular_keywords[:10], 1):
                st.write(f"{idx}. **{keyword}** - Used by {count} customer(s)")
        else:
            st.info("No keywords found")
    
    with col2:
        st.write("**Top RSS Feeds (Across All Customers):**")
        if popular_feeds:
            for idx, (feed_name, count) in enumerate(popular_feeds[:10], 1):
                st.write(f"{idx}. **{feed_name}** - Used by {count} customer(s)")
        else:
            st.info("No RSS feeds found")
    
    st.markdown("---")
    
    st.write("**Most Active Customers (Last 30 Days):**")
    if active_customers:
        for idx, (customer_id, newsletter_count) in enumerate(active_customers[:10], 1):
            customer_info = next((c for c in all_customers if c.get('customer_id') == customer_id), None)
            company_name = customer_info.get('company_name', customer_id) if customer_info else customer_id
            st.write(f"{idx}. **{company_name}** ({customer_id}) - {newsletter_count} newsletter(s)")
    else:
        st.info("No active customers in the last 30 days")

def render_trend_analysis():
    """Show trend analysis"""
    st.subheader("Trend Analysis")
    
    all_customers = get_customer_list()
    
    if not all_customers:
        st.info("No customers found for trend analysis.")
        return
    
    # Customer retention
    retention_rate = calculate_retention_rate()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Customer Retention Rate", f"{retention_rate}%")
    
    with col2:
        active_customers = [c for c in all_customers if c.get('status', '').lower() == 'active']
        st.metric("Active Customers", len(active_customers))
    
    with col3:
        total_users = sum(
            len(get_customer_details(c.get('customer_id', '')).get('user_access', {}).get('users', []))
            for c in all_customers
        )
        st.metric("Total Users", total_users)
    
    st.markdown("---")
    
    # Tier distribution
    st.write("**Subscription Tier Distribution:**")
    tier_counts = Counter()
    for customer in all_customers:
        # Get tier directly from customer dict (info fields are spread)
        tier = customer.get('subscription_tier', 'Unknown')
        tier_counts[tier] += 1
    
    if tier_counts:
        for tier, count in tier_counts.most_common():
            st.write(f"**{tier}:** {count} customer(s)")

def get_popular_keywords(limit: int = 10) -> List[tuple]:
    """
    Get most popular keywords across all customers
    
    Args:
        limit: Maximum number of keywords to return
    
    Returns:
        List of (keyword, count) tuples sorted by count
    """
    all_customers = list_all_customers()
    keyword_counter = Counter()
    
    for customer_id in all_customers:
        details = get_customer_details(customer_id)
        if details:
            keywords = details.get('keywords', {}).get('keywords', [])
            keyword_counter.update(keywords)
    
    return keyword_counter.most_common(limit)

def get_popular_feeds(limit: int = 10) -> List[tuple]:
    """
    Get most popular RSS feeds across all customers
    
    Args:
        limit: Maximum number of feeds to return
    
    Returns:
        List of (feed_name, count) tuples sorted by count
    """
    all_customers = list_all_customers()
    feed_counter = Counter()
    
    for customer_id in all_customers:
        details = get_customer_details(customer_id)
        if details:
            feeds = details.get('feeds', {}).get('feeds', [])
            for feed in feeds:
                if feed.get('enabled', True):
                    feed_name = feed.get('name', feed.get('url', 'Unknown'))
                    feed_counter[feed_name] += 1
    
    return feed_counter.most_common(limit)

def get_most_active_customers(days: int = 30) -> List[tuple]:
    """
    Get most active customers by newsletter count
    
    Args:
        days: Number of days to look back
    
    Returns:
        List of (customer_id, newsletter_count) tuples sorted by count
    """
    all_customers = list_all_customers()
    customer_activity = []
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for customer_id in all_customers:
        newsletters = list_customer_files(customer_id, "data/newsletters")
        newsletter_count = len([f for f in newsletters if f.get('name', '').endswith('.html')])
        
        # Filter by date if needed (simple version - just count all)
        # Could be enhanced to filter by last_modified
        if newsletter_count > 0:
            customer_activity.append((customer_id, newsletter_count))
    
    # Sort by count (descending)
    customer_activity.sort(key=lambda x: x[1], reverse=True)
    
    return customer_activity

def calculate_retention_rate() -> float:
    """
    Calculate customer retention rate
    
    Returns:
        Retention rate as percentage
    """
    all_customers = get_customer_list()
    
    if not all_customers:
        return 0.0
    
    active_count = len([c for c in all_customers if c.get('status', '').lower() == 'active'])
    total_count = len(all_customers)
    
    if total_count == 0:
        return 0.0
    
    return round((active_count / total_count) * 100, 1)

def get_engagement_metrics(customer_id: str) -> Dict:
    """
    Get engagement metrics for a customer
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Dictionary with engagement metrics
    """
    details = get_customer_details(customer_id)
    if not details:
        return {}
    
    newsletters = list_customer_files(customer_id, "data/newsletters")
    newsletter_count = len([f for f in newsletters if f.get('name', '').endswith('.html')])
    
    keywords_count = len(details.get('keywords', {}).get('keywords', []))
    feeds_count = len(details.get('feeds', {}).get('feeds', []))
    users_count = len(details.get('user_access', {}).get('users', []))
    
    return {
        "newsletters": newsletter_count,
        "keywords": keywords_count,
        "feeds": feeds_count,
        "users": users_count,
        "engagement_score": newsletter_count * 2 + keywords_count + feeds_count + users_count
    }

