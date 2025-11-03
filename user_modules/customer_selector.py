"""
Customer Selector Module

Handles newsletter selection, user access management, and permissions checking
for the multi-tenant User App (GlobalNewsPilot).
"""

import streamlit as st
from typing import List, Dict, Optional, Tuple
from user_modules.github_user import get_all_user_access_files, load_config
import logging

logger = logging.getLogger(__name__)

def get_user_email() -> Optional[str]:
    """
    Get user email from session state
    
    Returns:
        User email string, or None if not set
    """
    return st.session_state.get('user_email')

def set_user_email(email: str):
    """Set user email in session state"""
    st.session_state.user_email = email

def get_user_newsletters(user_email: str) -> List[Dict]:
    """
    Get all newsletters the user has access to
    
    Scans all customer user_access.json files and returns newsletters
    where the user's email is found, along with their tier and permissions.
    
    Args:
        user_email: User's email address
    
    Returns:
        List of newsletter dictionaries:
        [
            {
                "customer_id": "htc",
                "name": "HTC Newsletter",
                "tier": "premium",
                "role": "admin",
                "permissions": ["view", "edit", "generate", "manage_config"],
                "added_date": "2025-01-15"
            },
            ...
        ]
    """
    if not user_email:
        return []
    
    user_newsletters = []
    all_access_files = get_all_user_access_files()
    
    for access_data in all_access_files:
        customer_id = access_data["customer_id"]
        user_access = access_data.get("user_access", {})
        users = user_access.get("users", [])
        
        # Find user in this customer's user list
        for user in users:
            if user.get("email", "").lower() == user_email.lower():
                # User found - get newsletter name from branding config
                branding = load_config(customer_id, "branding")
                newsletter_name = "Newsletter"
                if branding:
                    newsletter_name = branding.get("application_name", newsletter_name)
                
                user_newsletters.append({
                    "customer_id": customer_id,
                    "name": newsletter_name,
                    "tier": user.get("tier", "basic"),
                    "role": user.get("role", "viewer"),
                    "permissions": user.get("permissions", ["view"]),
                    "added_date": user.get("added_date", ""),
                    "added_by": user.get("added_by", ""),
                    "password": user.get("password", ""),  # Include password for authentication
                    "status": user.get("status", "Active"),
                    "valid_until": user.get("valid_until", "")
                })
                break
    
    # Sort by name for consistent display
    user_newsletters.sort(key=lambda x: x["name"])
    return user_newsletters

def authenticate_user(user_email: str, password: str) -> Tuple[bool, str, Optional[Dict]]:
    """
    Authenticate user with email and password
    
    Args:
        user_email: User's email address
        password: User's password
    
    Returns:
        Tuple of (is_authenticated, error_message, user_data)
        user_data is None if authentication fails
    """
    if not user_email or not password:
        return False, "Email and password are required.", None
    
    # Get user's newsletters (includes password from user_access.json)
    user_newsletters = get_user_newsletters(user_email)
    
    if not user_newsletters:
        return False, "Invalid email or password.", None
    
    # Check password (check first newsletter's password - should be same across all)
    # In practice, user should only be in one customer, but we check all
    user_found = None
    for newsletter in user_newsletters:
        stored_password = newsletter.get("password", "")
        if stored_password == password:
            user_found = newsletter
            break
    
    if not user_found:
        return False, "Invalid email or password.", None
    
    # Check account status
    status = user_found.get("status", "Active").strip()
    if status.lower() != "active":
        return False, "Your account is not active. Contact administrator.", None
    
    # Check expiration date (if provided)
    valid_until_str = user_found.get("valid_until", "").strip()
    if valid_until_str:
        try:
            from datetime import datetime
            # Support multiple date formats
            date_formats = ["%d/%m/%Y", "%Y-%m-%d", "%m/%d/%Y"]
            valid_until = None
            for fmt in date_formats:
                try:
                    valid_until = datetime.strptime(valid_until_str, fmt).date()
                    break
                except ValueError:
                    continue
            
            if valid_until and valid_until < datetime.now().date():
                return False, "Your account has expired. Contact administrator.", None
        except Exception:
            # If date parsing fails, skip expiration check
            pass
    
    return True, "", user_found

def is_user_logged_in_elsewhere(user_email: str) -> bool:
    """
    Check if user is already logged in elsewhere (single session per email)
    
    This checks a sessions tracking file in GitHub.
    For now, we'll use a simple approach - store active sessions in GitHub.
    
    Args:
        user_email: User's email address
    
    Returns:
        True if user is already logged in, False otherwise
    """
    # TODO: Implement session tracking in GitHub
    # For now, return False (allow multiple sessions during development)
    # Later, we'll track active sessions in customers/{customer_id}/data/sessions.json
    return False

def get_user_permissions(user_email: str, customer_id: str) -> Dict:
    """
    Get user's tier and permissions for a specific newsletter
    
    Args:
        user_email: User's email address
        customer_id: Customer identifier
    
    Returns:
        Dictionary with tier, role, and permissions:
        {
            "tier": "premium",
            "role": "admin",
            "permissions": ["view", "edit", "generate", "manage_config"]
        }
        Returns empty dict if user not found
    """
    if not user_email or not customer_id:
        return {}
    
    from user_modules.github_user import load_user_access
    
    user_access = load_user_access(customer_id)
    if not user_access:
        return {}
    
    users = user_access.get("users", [])
    for user in users:
        if user.get("email", "").lower() == user_email.lower():
            return {
                "tier": user.get("tier", "basic"),
                "role": user.get("role", "viewer"),
                "permissions": user.get("permissions", ["view"])
            }
    
    return {}

def set_current_customer(customer_id: str):
    """Set current customer in session state"""
    st.session_state.current_customer_id = customer_id
    # Clear cached config when switching customers
    if 'customer_config_cache' in st.session_state:
        del st.session_state.customer_config_cache

def get_current_customer() -> Optional[str]:
    """Get current customer ID from session state"""
    return st.session_state.get('current_customer_id')

def load_customer_config(customer_id: str) -> Dict:
    """
    Load customer configuration (branding, keywords, feeds)
    Uses caching to avoid repeated GitHub API calls
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Dictionary with all customer configs:
        {
            "branding": {...},
            "keywords": {...},
            "feeds": {...}
        }
    """
    # Check cache first
    cache_key = f'customer_config_{customer_id}'
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Load all configs
    config = {
        "branding": load_config(customer_id, "branding") or {},
        "keywords": load_config(customer_id, "keywords") or {},
        "feeds": load_config(customer_id, "feeds") or {}
    }
    
    # Cache it
    st.session_state[cache_key] = config
    return config

def has_permission(user_email: str, customer_id: str, permission_name: str) -> bool:
    """
    Check if user has a specific permission for a newsletter
    
    Args:
        user_email: User's email address
        customer_id: Customer identifier
        permission_name: Permission to check (e.g., "edit_config", "generate", "view")
    
    Returns:
        True if user has permission, False otherwise
    """
    permissions = get_user_permissions(user_email, customer_id)
    user_permissions = permissions.get("permissions", [])
    
    # "view" is always allowed if user has access
    if permission_name == "view":
        return len(user_permissions) > 0
    
    return permission_name in user_permissions

def render_newsletter_selector(user_newsletters: List[Dict], current_customer_id: Optional[str] = None) -> Optional[str]:
    """
    Render newsletter selector in sidebar (always visible)
    
    Args:
        user_newsletters: List of newsletters user has access to
        current_customer_id: Currently selected customer ID
    
    Returns:
        Selected customer_id, or None if selection changed (trigger rerun)
    """
    if not user_newsletters:
        return None
    
    # Create options dictionary
    newsletter_options = {n['name']: n['customer_id'] for n in user_newsletters}
    newsletter_names = list(newsletter_options.keys())
    
    # Find current index
    if current_customer_id:
        current_index = next(
            (i for i, n in enumerate(user_newsletters) 
             if n['customer_id'] == current_customer_id),
            0
        )
    else:
        current_index = 0
        # Auto-select first newsletter if none selected
        if user_newsletters:
            set_current_customer(user_newsletters[0]['customer_id'])
            return user_newsletters[0]['customer_id']
    
    # Render selectbox
    selected_name = st.sidebar.selectbox(
        "📰 Switch Newsletter",
        newsletter_names,
        index=current_index,
        key="newsletter_selector_sidebar"
    )
    
    # Get selected customer ID
    selected_customer_id = newsletter_options[selected_name]
    
    # Check if selection changed
    if selected_customer_id != current_customer_id:
        set_current_customer(selected_customer_id)
        
        # Sync dashboard selectbox widget if it exists (update its index)
        dashboard_key = "newsletter_selector_dashboard"
        if dashboard_key in st.session_state:
            selected_index = newsletter_names.index(selected_name)
            st.session_state[dashboard_key] = selected_index
        
        st.rerun()
    
    return selected_customer_id

def switch_newsletter(customer_id: str):
    """
    Switch to a different newsletter (programmatic)
    
    Args:
        customer_id: Customer identifier to switch to
    """
    set_current_customer(customer_id)
    st.rerun()

def get_permission_tier_requirements() -> Dict[str, List[str]]:
    """
    Get permission requirements by tier
    
    Returns:
        Dictionary mapping tiers to required permission lists
    """
    return {
        "premium": ["view", "edit", "generate", "manage_config", "edit_config"],
        "standard": ["view", "generate"],
        "basic": ["view"]
    }

def check_tier_permissions(tier: str, required_permission: str) -> bool:
    """
    Check if tier has required permission
    
    Args:
        tier: User tier (premium, standard, basic)
        required_permission: Permission to check
    
    Returns:
        True if tier has permission, False otherwise
    """
    tier_reqs = get_permission_tier_requirements()
    tier_perms = tier_reqs.get(tier.lower(), ["view"])
    return required_permission in tier_perms

