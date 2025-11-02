"""
Config Viewer Module

View and edit customer configurations with history tracking.
"""

import streamlit as st
from typing import Dict, List, Optional
from admin_modules.github_admin import (
    fetch_customer_config,
    update_customer_config,
    get_commit_history,
    list_all_customers
)
from admin_modules.customer_manager import get_customer_details
import json
from datetime import datetime

def render_config_viewer():
    """Render configuration viewer interface"""
    st.header("Configuration Viewer")
    
    # Customer selector
    all_customer_ids = ["-- Select Customer --"] + list_all_customers()
    selected_customer = st.selectbox(
        "Select Customer",
        all_customer_ids,
        key="config_viewer_customer"
    )
    
    if selected_customer == "-- Select Customer --":
        st.info("Please select a customer to view their configuration.")
        return
    
    # Get customer details
    customer_details = get_customer_details(selected_customer)
    if not customer_details:
        st.error("Failed to load customer details")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["Keywords", "RSS Feeds", "Branding", "History"])
    
    with tab1:
        render_keywords_config(selected_customer, customer_details.get('keywords', {}))
    
    with tab2:
        render_feeds_config(selected_customer, customer_details.get('feeds', {}))
    
    with tab3:
        render_branding_config(selected_customer, customer_details.get('branding', {}))
    
    with tab4:
        render_config_history(selected_customer)

def render_keywords_config(customer_id: str, keywords_data: Dict):
    """Render keywords configuration editor"""
    st.subheader("Keywords Configuration")
    
    keywords = keywords_data.get('keywords', [])
    
    st.write(f"**Current Keywords ({len(keywords)}):**")
    
    if keywords:
        # Display keywords
        cols = st.columns(min(len(keywords), 4))
        for idx, keyword in enumerate(keywords):
            with cols[idx % len(cols)]:
                st.write(f"• {keyword}")
    
    st.markdown("---")
    
    # Edit keywords
    st.write("**Edit Keywords:**")
    
    # Get new keywords input (comma-separated or one at a time)
    new_keywords_input = st.text_area(
        "Enter keywords (one per line or comma-separated)",
        value="\n".join(keywords),
        height=100,
        key="keywords_textarea"
    )
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("💾 Save Keywords", key="save_keywords"):
            # Parse keywords
            if new_keywords_input:
                # Split by newline or comma
                new_keywords = []
                for line in new_keywords_input.split('\n'):
                    if ',' in line:
                        new_keywords.extend([k.strip() for k in line.split(',') if k.strip()])
                    else:
                        if line.strip():
                            new_keywords.append(line.strip())
                
                # Remove duplicates (case-insensitive)
                seen = set()
                unique_keywords = []
                for kw in new_keywords:
                    if kw.lower() not in seen:
                        seen.add(kw.lower())
                        unique_keywords.append(kw)
                
                # Update
                keywords_data['keywords'] = unique_keywords
                keywords_data['last_updated'] = 'admin'
                keywords_data['updated_at'] = datetime.now().isoformat()
                
                if update_customer_config(customer_id, "keywords", keywords_data, f"Admin: Update keywords for {customer_id}"):
                    st.success("Keywords saved successfully!")
                    st.rerun()
            else:
                # Save empty list
                keywords_data['keywords'] = []
                keywords_data['last_updated'] = 'admin'
                keywords_data['updated_at'] = datetime.now().isoformat()
                
                if update_customer_config(customer_id, "keywords", keywords_data, f"Admin: Clear keywords for {customer_id}"):
                    st.success("Keywords cleared!")
                    st.rerun()

def render_feeds_config(customer_id: str, feeds_data: Dict):
    """Render RSS feeds configuration editor"""
    st.subheader("RSS Feeds Configuration")
    
    feeds = feeds_data.get('feeds', [])
    
    st.write(f"**Current Feeds ({len(feeds)}):**")
    
    if feeds:
        for idx, feed in enumerate(feeds):
            with st.expander(f"**{feed.get('name', 'Unnamed Feed')}**"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    feed_name = st.text_input("Feed Name", value=feed.get('name', ''), key=f"feed_name_{idx}")
                    feed_url = st.text_input("Feed URL", value=feed.get('url', ''), key=f"feed_url_{idx}")
                    feed_enabled = st.checkbox("Enabled", value=feed.get('enabled', True), key=f"feed_enabled_{idx}")
                
                with col2:
                    if st.button("💾 Update", key=f"update_feed_{idx}"):
                        if feed_name and feed_url:
                            if feed_url.startswith(("http://", "https://")):
                                feeds[idx] = {
                                    "name": feed_name,
                                    "url": feed_url,
                                    "enabled": feed_enabled
                                }
                                feeds_data['feeds'] = feeds
                                feeds_data['last_updated'] = 'admin'
                                feeds_data['updated_at'] = datetime.now().isoformat()
                                
                                if update_customer_config(customer_id, "feeds", feeds_data, f"Admin: Update feed for {customer_id}"):
                                    st.success("Feed updated!")
                                    st.rerun()
                            else:
                                st.error("URL must start with http:// or https://")
                    
                    if st.button("🗑️ Delete", key=f"delete_feed_{idx}"):
                        feeds.remove(feed)
                        feeds_data['feeds'] = feeds
                        feeds_data['last_updated'] = 'admin'
                        feeds_data['updated_at'] = datetime.now().isoformat()
                        
                        if update_customer_config(customer_id, "feeds", feeds_data, f"Admin: Delete feed for {customer_id}"):
                            st.success("Feed deleted!")
                            st.rerun()
    
    st.markdown("---")
    
    # Add new feed
    st.write("**Add New Feed:**")
    col1, col2 = st.columns(2)
    with col1:
        new_feed_name = st.text_input("Feed Name", key="new_feed_name_viewer")
    with col2:
        new_feed_url = st.text_input("Feed URL", key="new_feed_url_viewer", placeholder="https://example.com/rss")
    
    if st.button("➕ Add Feed", key="add_feed_viewer"):
        if new_feed_name and new_feed_url:
            if new_feed_url.startswith(("http://", "https://")):
                feeds.append({
                    "name": new_feed_name,
                    "url": new_feed_url,
                    "enabled": True
                })
                feeds_data['feeds'] = feeds
                feeds_data['last_updated'] = 'admin'
                feeds_data['updated_at'] = datetime.now().isoformat()
                
                if update_customer_config(customer_id, "feeds", feeds_data, f"Admin: Add feed for {customer_id}"):
                    st.success("Feed added!")
                    st.rerun()
            else:
                st.error("URL must start with http:// or https://")
        else:
            st.warning("Please enter both name and URL")

def render_branding_config(customer_id: str, branding_data: Dict):
    """Render branding configuration editor"""
    st.subheader("Branding Configuration")
    
    with st.form("branding_form"):
        application_name = st.text_input(
            "Application Name",
            value=branding_data.get('application_name', ''),
            key="branding_app_name"
        )
        short_name = st.text_input(
            "Short Name",
            value=branding_data.get('short_name', ''),
            key="branding_short_name"
        )
        newsletter_title_template = st.text_input(
            "Newsletter Title Template",
            value=branding_data.get('newsletter_title_template', '{name} - Week {week}'),
            key="branding_title_template",
            help="Use {name} and {week} as placeholders"
        )
        footer_text = st.text_input(
            "Footer Text",
            value=branding_data.get('footer_text', ''),
            key="branding_footer_text"
        )
        footer_url = st.text_input(
            "Footer URL",
            value=branding_data.get('footer_url', ''),
            key="branding_footer_url"
        )
        footer_url_display = st.text_input(
            "Footer URL Display Text",
            value=branding_data.get('footer_url_display', ''),
            key="branding_footer_url_display"
        )
        
        if st.form_submit_button("💾 Save Branding"):
            branding_data.update({
                'application_name': application_name,
                'short_name': short_name,
                'newsletter_title_template': newsletter_title_template,
                'footer_text': footer_text,
                'footer_url': footer_url,
                'footer_url_display': footer_url_display
            })
            
            if update_customer_config(customer_id, "branding", branding_data, f"Admin: Update branding for {customer_id}"):
                st.success("Branding saved successfully!")
                st.rerun()

def render_config_history(customer_id: str):
    """Render configuration change history"""
    st.subheader("Configuration History")
    
    st.write("**Recent Changes:**")
    
    # Get commit history for config files
    config_files = ["keywords.json", "feeds.json", "branding.json"]
    
    all_history = []
    for config_file in config_files:
        history = get_commit_history(customer_id, f"config/{config_file}", limit=5)
        for commit in history:
            commit['config_file'] = config_file
            all_history.append(commit)
    
    # Sort by date (newest first)
    all_history.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    if all_history:
        for commit in all_history[:20]:  # Show last 20 changes
            with st.expander(f"**{commit.get('config_file')}** - {commit.get('message', 'No message')[:50]}"):
                st.write(f"**Author:** {commit.get('author', 'Unknown')}")
                st.write(f"**Date:** {commit.get('date', 'Unknown')}")
                st.write(f"**Message:** {commit.get('message', 'No message')}")
                if commit.get('url'):
                    st.markdown(f"[View on GitHub]({commit['url']})")
    else:
        st.info("No configuration history found.")

