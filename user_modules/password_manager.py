"""
Password Manager Module

Handles password changes for users in the User App.
"""

import streamlit as st
from typing import Tuple
from user_modules.github_user import load_user_access, save_config_auto
from user_modules.customer_selector import get_current_customer, get_user_email
import logging

logger = logging.getLogger(__name__)

def change_password(customer_id: str, user_email: str, old_password: str, new_password: str, confirm_password: str) -> Tuple[bool, str]:
    """
    Change user password
    
    Args:
        customer_id: Customer identifier
        user_email: User's email address
        old_password: Current password (for verification)
        new_password: New password
        confirm_password: Confirm new password
    
    Returns:
        Tuple of (success, message)
    """
    # Validate inputs
    if not old_password or not new_password or not confirm_password:
        return False, "All password fields are required."
    
    # Check old password matches
    user_access = load_user_access(customer_id)
    if not user_access:
        return False, "Failed to load user data."
    
    users = user_access.get("users", [])
    user_found = None
    
    for user in users:
        if user.get("email", "").lower() == user_email.lower():
            user_found = user
            break
    
    if not user_found:
        return False, "User not found."
    
    # Verify old password
    stored_password = user_found.get("password", "")
    if stored_password != old_password:
        return False, "Current password is incorrect."
    
    # Check new password matches confirmation
    if new_password != confirm_password:
        return False, "New password and confirmation do not match."
    
    # Check password is not the same as old
    if new_password == old_password:
        return False, "New password must be different from current password."
    
    # Validate password length (basic validation)
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters long."
    
    # Update password
    user_found["password"] = new_password
    
    # Save updated user_access.json
    try:
        # Use save_config_auto for user_access.json (it's in customers/{customer_id}/ folder)
        # Actually, user_access.json is not a "config" file, but we can reuse the save function
        # We need to save it properly - let's add a function to github_user.py for this
        
        # For now, update in memory and we'll save via GitHub
        # We'll create a specific function for saving user_access.json
        success = save_user_access(customer_id, user_access)
        
        if success:
            return True, "Password changed successfully!"
        else:
            return False, "Failed to save password. Please try again."
    
    except Exception as e:
        logger.error(f"Error changing password: {e}")
        return False, f"Error changing password: {str(e)}"

def save_user_access(customer_id: str, user_access_data: dict) -> bool:
    """
    Save user_access.json to GitHub
    
    Args:
        customer_id: Customer identifier
        user_access_data: User access data dictionary
    
    Returns:
        True if successful, False otherwise
    """
    from user_modules.github_user import get_repo
    import json
    
    try:
        repo = get_repo()
        if not repo:
            return False
        
        access_path = f"customers/{customer_id}/user_access.json"
        content = json.dumps(user_access_data, indent=2, ensure_ascii=False)
        commit_message = f"Update user password for {customer_id}"
        
        try:
            file = repo.get_contents(access_path)
            repo.update_file(
                access_path,
                commit_message,
                content,
                file.sha
            )
        except Exception as e:
            if "404" in str(e):
                # File doesn't exist, create it
                repo.create_file(
                    access_path,
                    commit_message,
                    content
                )
            else:
                raise
        
        logger.info(f"User access saved: {access_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving user access: {e}")
        return False

def render_password_change(customer_id: str, user_email: str):
    """
    Render password change interface
    
    Args:
        customer_id: Customer identifier
        user_email: User's email address
    """
    st.subheader("🔐 Change Password")
    st.info("Update your password. This change will be saved immediately.")
    
    with st.form("change_password_form"):
        old_password = st.text_input("Current Password", type="password", key="old_pw")
        new_password = st.text_input("New Password", type="password", key="new_pw")
        confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pw")
        
        submitted = st.form_submit_button("Change Password", type="primary")
        
        if submitted:
            success, message = change_password(
                customer_id,
                user_email,
                old_password,
                new_password,
                confirm_password
            )
            
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

