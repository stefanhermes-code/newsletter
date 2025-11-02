"""
Config Manager Module

Manages customer configuration (keywords, RSS feeds) with background saving.
Only accessible to users with 'edit_config' permission.
"""

import streamlit as st
from typing import List, Dict, Optional, Tuple
from user_modules.github_user import load_config, save_config_auto
from user_modules.customer_selector import has_permission, get_current_customer
import logging

logger = logging.getLogger(__name__)

def load_keywords(customer_id: str) -> List[str]:
    """
    Load keywords from GitHub
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        List of keyword strings
    """
    keywords_config = load_config(customer_id, "keywords")
    if not keywords_config:
        return []
    
    return keywords_config.get("keywords", [])

def load_feeds(customer_id: str) -> List[Dict]:
    """
    Load RSS feeds from GitHub
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        List of feed dictionaries:
        [
            {"name": "...", "url": "...", "enabled": True},
            ...
        ]
    """
    feeds_config = load_config(customer_id, "feeds")
    if not feeds_config:
        return []
    
    return feeds_config.get("feeds", [])

def save_keywords(customer_id: str, keywords: List[str]) -> bool:
    """
    Save keywords to GitHub (background save)
    
    Args:
        customer_id: Customer identifier
        keywords: List of keyword strings
    
    Returns:
        True if successful, False otherwise
    """
    try:
        keywords_data = {
            "keywords": keywords,
            "last_updated": st.session_state.get('user_email', 'unknown'),
            "updated_at": st.session_state.get('update_timestamp', '')
        }
        
        return save_config_auto(customer_id, "keywords", keywords_data)
    except Exception as e:
        logger.error(f"Error saving keywords for {customer_id}: {e}")
        return False

def save_feeds(customer_id: str, feeds: List[Dict]) -> bool:
    """
    Save RSS feeds to GitHub (background save)
    
    Args:
        customer_id: Customer identifier
        feeds: List of feed dictionaries
    
    Returns:
        True if successful, False otherwise
    """
    try:
        feeds_data = {
            "feeds": feeds,
            "last_updated": st.session_state.get('user_email', 'unknown'),
            "updated_at": st.session_state.get('update_timestamp', '')
        }
        
        return save_config_auto(customer_id, "feeds", feeds_data)
    except Exception as e:
        logger.error(f"Error saving feeds for {customer_id}: {e}")
        return False

def validate_keywords(keywords: List[str]) -> Tuple[bool, str]:
    """
    Validate keywords before saving
    
    Args:
        keywords: List of keyword strings
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not keywords:
        return True, ""  # Empty is allowed
    
    # Check for duplicates
    if len(keywords) != len(set(keywords)):
        return False, "Duplicate keywords found. Please remove duplicates."
    
    # Check for empty strings
    if any(not k.strip() for k in keywords):
        return False, "Empty keywords are not allowed. Please remove empty entries."
    
    # Check length
    for keyword in keywords:
        if len(keyword) > 100:
            return False, f"Keyword '{keyword}' is too long (max 100 characters)."
    
    return True, ""

def validate_feeds(feeds: List[Dict]) -> Tuple[bool, str]:
    """
    Validate RSS feeds before saving
    
    Args:
        feeds: List of feed dictionaries
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not feeds:
        return True, ""  # Empty is allowed
    
    # Check required fields
    for feed in feeds:
        if not feed.get("name") or not feed.get("url"):
            return False, "All feeds must have both a name and URL."
        
        # Basic URL validation
        url = feed.get("url", "")
        if not url.startswith(("http://", "https://")):
            return False, f"Invalid URL format for feed '{feed.get('name')}'. Must start with http:// or https://"
    
    # Check for duplicate URLs
    urls = [f.get("url") for f in feeds]
    if len(urls) != len(set(urls)):
        return False, "Duplicate feed URLs found. Please remove duplicates."
    
    return True, ""

def load_branding(customer_id: str) -> Dict:
    """
    Load branding configuration from GitHub
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Dictionary with branding settings
    """
    branding_config = load_config(customer_id, "branding")
    if not branding_config:
        return {}
    
    return branding_config

def save_branding(customer_id: str, branding_data: Dict, user_email: Optional[str] = None) -> bool:
    """
    Save branding configuration to GitHub (background save)
    
    Args:
        customer_id: Customer identifier
        branding_data: Branding configuration dictionary
        user_email: Optional user email for tracking updates
    
    Returns:
        True if saved successfully, False otherwise
    """
    # Add metadata
    from datetime import datetime
    branding_data['last_updated'] = user_email or 'user'
    branding_data['updated_at'] = datetime.now().isoformat()
    
    # Save to GitHub
    return save_config_auto(
        customer_id,
        "branding",
        branding_data,
        f"User: Update branding configuration"
    )

def render_keywords_editor(customer_id: str, user_email: str):
    """
    Render keywords editor interface
    
    Args:
        customer_id: Customer identifier
        user_email: User email for permission check
    """
    if not has_permission(user_email, customer_id, "edit_config"):
        st.error("You don't have permission to edit keywords. Premium tier required.")
        return
    
    st.subheader("Keywords Configuration")
    st.info("Keywords are used for Google News searches. Add or remove keywords as needed.")
    
    # Load current keywords
    keywords = load_keywords(customer_id)
    
    # Editor interface
    st.write("**Current Keywords:**")
    
    if not keywords:
        st.info("No keywords configured yet. Add your first keyword below.")
    
    # Keyword input
    new_keyword = st.text_input("Add New Keyword", key="new_keyword_input")
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("➕ Add", key="add_keyword"):
            if new_keyword and new_keyword.strip():
                keyword_lower = new_keyword.strip().lower()
                if keyword_lower not in [k.lower() for k in keywords]:
                    keywords.append(new_keyword.strip())
                    # Auto-save
                    if save_keywords(customer_id, keywords):
                        st.success(f"Keyword '{new_keyword.strip()}' added and saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save keyword.")
                else:
                    st.warning("Keyword already exists.")
            else:
                st.warning("Please enter a keyword.")
    
    # Display keywords with delete option
    if keywords:
        st.markdown("---")
        st.write("**Manage Keywords:**")
        
        # Display in columns for better layout
        cols = st.columns(min(len(keywords), 3))
        for idx, keyword in enumerate(keywords):
            with cols[idx % len(cols)]:
                col_del, col_keyword = st.columns([1, 4])
                with col_keyword:
                    st.write(f"• {keyword}")
                with col_del:
                    if st.button("🗑️", key=f"delete_keyword_{idx}"):
                        keywords.remove(keyword)
                        if save_keywords(customer_id, keywords):
                            st.success(f"Keyword '{keyword}' removed and saved!")
                            st.rerun()
                        else:
                            st.error("Failed to save changes.")

def render_feeds_editor(customer_id: str, user_email: str):
    """
    Render RSS feeds editor interface
    
    Args:
        customer_id: Customer identifier
        user_email: User email for permission check
    """
    if not has_permission(user_email, customer_id, "edit_config"):
        st.error("You don't have permission to edit RSS feeds. Premium tier required.")
        return
    
    st.subheader("RSS Feeds Configuration")
    st.info("RSS feeds are used as a secondary source for news finding. Add or remove feeds as needed.")
    
    # Load current feeds
    feeds = load_feeds(customer_id)
    
    # Add new feed form
    with st.expander("➕ Add New RSS Feed", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            feed_name = st.text_input("Feed Name", key="new_feed_name")
        with col2:
            feed_url = st.text_input("Feed URL", key="new_feed_url", placeholder="https://example.com/rss")
        
        if st.button("Add Feed", key="add_feed_button"):
            if feed_name and feed_url:
                # Validate
                test_feed = [{"name": feed_name, "url": feed_url, "enabled": True}]
                is_valid, error_msg = validate_feeds(test_feed)
                
                if is_valid:
                    feeds.append({"name": feed_name, "url": feed_url, "enabled": True})
                    if save_feeds(customer_id, feeds):
                        st.success(f"Feed '{feed_name}' added and saved!")
                        st.rerun()
                    else:
                        st.error("Failed to save feed.")
                else:
                    st.error(error_msg)
            else:
                st.warning("Please enter both name and URL.")
    
    # Display feeds
    if not feeds:
        st.info("No RSS feeds configured yet. Use the 'Add New RSS Feed' section above to add feeds.")
    else:
        st.markdown("---")
        st.write(f"**Current RSS Feeds ({len(feeds)}):**")
        
        for idx, feed in enumerate(feeds):
            with st.container():
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.write(f"**{feed.get('name', 'Unnamed Feed')}**")
                
                with col2:
                    st.caption(f"🔗 [Open Feed]({feed.get('url', '#')})")
                
                with col3:
                    enabled = st.checkbox(
                        "Enabled",
                        value=feed.get('enabled', True),
                        key=f"feed_enabled_{idx}"
                    )
                    if enabled != feed.get('enabled', True):
                        feed['enabled'] = enabled
                        save_feeds(customer_id, feeds)
                        st.rerun()
                
                with col4:
                    if st.button("🗑️ Delete", key=f"delete_feed_{idx}"):
                        feeds.remove(feed)
                        if save_feeds(customer_id, feeds):
                            st.success(f"Feed '{feed.get('name')}' removed and saved!")
                            st.rerun()
                        else:
                            st.error("Failed to save changes.")
                
                st.markdown("---")

def render_branding_editor(customer_id: str, user_email: str):
    """
    Render branding configuration editor
    
    Args:
        customer_id: Customer identifier
        user_email: User email for tracking updates
    """
    st.subheader("Branding Configuration")
    st.info("Customize how your newsletter appears. Changes take effect immediately for new newsletters.")
    
    # Load current branding
    branding_data = load_branding(customer_id)
    
    if not branding_data:
        st.warning("Branding configuration not found. Using defaults.")
        branding_data = {
            'application_name': '',
            'newsletter_title_template': '{name} - Week {week}',
            'footer_text': '',
            'footer_url': '',
            'footer_url_display': ''
        }
    
    # Editor form
    with st.form("branding_editor_form"):
        application_name = st.text_input(
            "Application Name *",
            value=branding_data.get('application_name', ''),
            help="This name appears in your newsletter and dashboard",
            key="branding_app_name_form"
        )
        
        newsletter_title_template = st.text_input(
            "Newsletter Title Template",
            value=branding_data.get('newsletter_title_template', '{name} - Week {week}'),
            help="Template for newsletter titles. Use {name} for application name and {week} for week number. Example: '{name} - Week {week}'",
            key="branding_title_template_form"
        )
        
        st.markdown("---")
        st.write("**Footer Settings (Optional)**")
        
        footer_text = st.text_input(
            "Footer Text",
            value=branding_data.get('footer_text', ''),
            help="Text that appears at the bottom of newsletters",
            key="branding_footer_text_form"
        )
        
        footer_url = st.text_input(
            "Footer URL",
            value=branding_data.get('footer_url', ''),
            help="Company website URL (must start with http:// or https://)",
            key="branding_footer_url_form"
        )
        
        footer_url_display = st.text_input(
            "Footer URL Display Text",
            value=branding_data.get('footer_url_display', ''),
            help="Display text for footer link. Example: 'www.example.com'",
            key="branding_footer_url_display_form"
        )
        
        submitted = st.form_submit_button("💾 Save Branding", type="primary")
        
        if submitted:
            # Validate required fields
            if not application_name or not application_name.strip():
                st.error("Application Name is required.")
                return
            
            # Validate URL if provided
            if footer_url and footer_url.strip():
                if not footer_url.strip().startswith(('http://', 'https://')):
                    st.error("Footer URL must start with http:// or https://")
                    return
            
            # Prepare branding data (don't overwrite short_name - admin-only)
            updated_branding = {
                'application_name': application_name.strip(),
                'newsletter_title_template': newsletter_title_template.strip(),
                'footer_text': footer_text.strip(),
                'footer_url': footer_url.strip(),
                'footer_url_display': footer_url_display.strip()
            }
            
            # Preserve short_name if it exists (admin-only field)
            if 'short_name' in branding_data:
                updated_branding['short_name'] = branding_data['short_name']
            
            # Save
            if save_branding(customer_id, updated_branding, user_email):
                st.success("✅ Branding configuration saved successfully!")
                st.info("Changes will be reflected in the next newsletter you generate.")
                st.rerun()
            else:
                st.error("Failed to save branding configuration. Please try again.")

def render_configuration_page(customer_id: str, user_email: str):
    """
    Render full configuration page with tabs
    
    Args:
        customer_id: Customer identifier
        user_email: User email for permission check
    """
    if not has_permission(user_email, customer_id, "edit_config"):
        st.error("You don't have permission to edit configuration. Premium tier required.")
        st.info("Contact your administrator to upgrade your account to Premium tier.")
        return
    
    st.title("Configuration Management")
    st.caption("Changes are saved automatically in the background")
    
    tab1, tab2 = st.tabs(["Keywords", "RSS Feeds"])
    
    with tab1:
        render_keywords_editor(customer_id, user_email)
    
    with tab2:
        render_feeds_editor(customer_id, user_email)

