"""
Admin Authentication Module

Handles authentication for Admin App (GNP_Admin).
Uses Streamlit secrets for admin credentials.
"""

import streamlit as st
from typing import Tuple, Optional

def check_admin_authentication() -> bool:
    """
    Check if admin is authenticated
    
    Returns:
        True if authenticated, False otherwise
    """
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    return st.session_state.admin_authenticated

def authenticate_admin(username: str, password: str) -> Tuple[bool, str]:
    """
    Authenticate admin user
    
    Args:
        username: Admin username
        password: Admin password
    
    Returns:
        Tuple of (is_authenticated, error_message)
    """
    # Get admin credentials from Streamlit secrets
    try:
        admin_username = st.secrets.get("admin_username", "admin")
        admin_password = st.secrets.get("admin_password", "")
        
        # If no password set in secrets, show error
        if not admin_password:
            return False, "Admin password not configured in Streamlit secrets. Please set 'admin_password' in secrets."
        
        # Check credentials
        if username == admin_username and password == admin_password:
            return True, ""
        else:
            return False, "Invalid username or password."
    
    except Exception as e:
        return False, f"Authentication error: {str(e)}"

def render_login_page():
    """Render admin login page"""
    # Display GNP logo at top
    import os
    logo_paths = [
        "assets/GNP Logo.png",  # GitHub location (primary)
        "assets/GNP logo.png",
        "GNP Logo.png",  # Root directory (local fallback)
        "GNP logo.png"
    ]
    logo_displayed = False
    for logo_path in logo_paths:
        if os.path.exists(logo_path):
            try:
                st.image(logo_path, use_container_width=True)
                logo_displayed = True
                break
            except Exception as e:
                continue
    # If not found locally, try to display anyway (for Streamlit Cloud)
    if not logo_displayed:
        for logo_path in logo_paths:
            try:
                st.image(logo_path, use_container_width=True)
                break
            except:
                continue
    
    st.title("🔐 Admin Dashboard - Login")
    st.markdown("Please enter your admin credentials to access the dashboard.")
    
    with st.form("admin_login_form"):
        username = st.text_input("Username", key="admin_username_input")
        password = st.text_input("Password", type="password", key="admin_password_input")
        
        submitted = st.form_submit_button("Login", type="primary")
        
        if submitted:
            if username and password:
                is_authenticated, error_message = authenticate_admin(username, password)
                
                if is_authenticated:
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_username = username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(error_message)
            else:
                st.error("Please enter both username and password.")
    
    # Legal disclaimer
    st.caption("By accessing this admin dashboard, you confirm you have authorization to manage customer data and configurations.")

def logout_admin():
    """Logout admin user"""
    st.session_state.admin_authenticated = False
    st.session_state.admin_username = None
    # Clear any other session state if needed
    st.rerun()

