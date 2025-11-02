"""
Customer Manager Module

Handles customer CRUD operations, user access management, and customer list operations.
"""

import streamlit as st
from typing import List, Dict, Optional
from admin_modules.github_admin import (
    list_all_customers,
    get_customer_info,
    update_customer_info,
    get_user_access,
    update_user_access,
    fetch_customer_config,
    create_customer_folder
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Tier permissions mapping
TIER_PERMISSIONS = {
    "premium": ["view", "edit", "generate", "manage_config", "edit_config"],
    "standard": ["view", "generate"],
    "basic": ["view"]
}

def get_customer_list() -> List[Dict]:
    """
    Get list of all customers with their info
    
    Returns:
        List of customer dictionaries with basic info
    """
    customer_ids = list_all_customers()
    customers = []
    
    for customer_id in customer_ids:
        info = get_customer_info(customer_id)
        if info:
            customers.append({
                "customer_id": customer_id,
                **info
            })
        else:
            # Customer folder exists but no info file
            customers.append({
                "customer_id": customer_id,
                "company_name": customer_id.title(),
                "status": "Unknown"
            })
    
    return customers

def get_customer_details(customer_id: str) -> Optional[Dict]:
    """
    Get full customer details including all configs
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Dictionary with all customer data, or None if error
    """
    if not customer_id:
        return None
    
    details = {
        "customer_id": customer_id,
        "info": get_customer_info(customer_id) or {},
        "branding": fetch_customer_config(customer_id, "branding") or {},
        "keywords": fetch_customer_config(customer_id, "keywords") or {},
        "feeds": fetch_customer_config(customer_id, "feeds") or {},
        "user_access": get_user_access(customer_id) or {"users": []}
    }
    
    return details

def search_customers(query: str) -> List[Dict]:
    """
    Search customers by company name, ID, or email
    
    Args:
        query: Search query string
    
    Returns:
        List of matching customers
    """
    if not query:
        return get_customer_list()
    
    query_lower = query.lower()
    all_customers = get_customer_list()
    matching = []
    
    for customer in all_customers:
        # Search in customer_id
        if query_lower in customer.get("customer_id", "").lower():
            matching.append(customer)
            continue
        
        # Search in company_name
        if query_lower in customer.get("company_name", "").lower():
            matching.append(customer)
            continue
        
        # Search in contact email
        info = get_customer_info(customer["customer_id"])
        if info and query_lower in info.get("contact_email", "").lower():
            matching.append(customer)
            continue
    
    return matching

def filter_customers(status: str = "All") -> List[Dict]:
    """
    Filter customers by status
    
    Args:
        status: Status to filter by ("Active", "Inactive", "All")
    
    Returns:
        List of filtered customers
    """
    all_customers = get_customer_list()
    
    if status == "All":
        return all_customers
    
    filtered = []
    for customer in all_customers:
        customer_status = customer.get("status", "Unknown")
        if customer_status.lower() == status.lower():
            filtered.append(customer)
    
    return filtered

def set_customer_status(customer_id: str, status: str) -> bool:
    """
    Set customer status (Active/Inactive)
    
    Args:
        customer_id: Customer identifier
        status: New status ("Active" or "Inactive")
    
    Returns:
        True if successful, False otherwise
    """
    info = get_customer_info(customer_id)
    if not info:
        info = {}
    
    info["status"] = status
    info["status_updated"] = datetime.now().isoformat()
    
    return update_customer_info(customer_id, info, f"Admin: Set status to {status} for {customer_id}")

def create_customer_record(customer_data: Dict) -> bool:
    """
    Create new customer record
    
    Args:
        customer_data: Dictionary with customer data
    
    Returns:
        True if successful, False otherwise
    """
    customer_id = customer_data.get("customer_id")
    if not customer_id:
        st.error("Customer ID is required")
        return False
    
    # Additional validation (defensive - should already be validated in form)
    from admin_modules.validators import validate_customer_id, validate_email
    is_valid_id, id_error = validate_customer_id(customer_id)
    if not is_valid_id:
        st.error(f"Invalid Customer ID: {id_error}")
        return False
    
    # Validate email if provided
    contact_email = customer_data.get("contact_email", "").strip()
    if contact_email:
        is_valid_email, email_error = validate_email(contact_email)
        if not is_valid_email:
            st.error(f"Invalid Contact Email: {email_error}")
            return False
    
    # Check if customer already exists
    existing = list_all_customers()
    if customer_id in existing:
        st.error(f"Customer ID '{customer_id}' already exists")
        return False
    
    # Create folder structure
    if not create_customer_folder(customer_id):
        st.error("Failed to create customer folder structure")
        return False
    
    # Create customer_info.json
    customer_info = {
        "customer_id": customer_id,
        "company_name": customer_data.get("company_name", ""),
        "short_name": customer_data.get("short_name", ""),
        "status": "Active",
        "created_date": datetime.now().isoformat(),
        "contact_name": customer_data.get("contact_name", ""),
        "contact_email": customer_data.get("contact_email", ""),
        "phone": customer_data.get("phone", ""),
        "subscription_tier": customer_data.get("subscription_tier", "Standard")
    }
    
    success = update_customer_info(customer_id, customer_info, f"Admin: Create customer {customer_id}")
    
    if success:
        # Create branding.json
        branding = {
            "application_name": customer_data.get("application_name", ""),
            "short_name": customer_data.get("short_name", ""),
            "newsletter_title_template": customer_data.get("newsletter_title_template", "{name} - Week {week}"),
            "footer_text": customer_data.get("footer_text", ""),
            "footer_url": customer_data.get("footer_url", ""),
            "footer_url_display": customer_data.get("footer_url_display", "")
        }
        from admin_modules.github_admin import update_customer_config
        
        # Create branding.json
        if not update_customer_config(customer_id, "branding", branding, f"Admin: Create branding for {customer_id}"):
            st.warning(f"Warning: Failed to create branding.json for {customer_id}")
        
        # Create keywords.json (always create, even if empty)
        keywords_data = {
            "keywords": customer_data.get("keywords", []),
            "last_updated": "admin",
            "updated_at": datetime.now().isoformat()
        }
        if not update_customer_config(customer_id, "keywords", keywords_data, f"Admin: Create keywords for {customer_id}"):
            st.warning(f"Warning: Failed to create keywords.json for {customer_id}")
        
        # Create feeds.json (always create, even if empty)
        feeds_data = {
            "feeds": customer_data.get("feeds", []),
            "last_updated": "admin",
            "updated_at": datetime.now().isoformat()
        }
        if not update_customer_config(customer_id, "feeds", feeds_data, f"Admin: Create feeds for {customer_id}"):
            st.warning(f"Warning: Failed to create feeds.json for {customer_id}")
            # This is critical - return False if feeds.json creation fails
            return False
        
        # Create user_access.json with initial user (if provided)
        if customer_data.get("contact_email"):
            initial_user = {
                "email": customer_data.get("contact_email"),
                "password": customer_data.get("initial_password", "changeme123"),
                "tier": customer_data.get("subscription_tier", "Standard").lower(),
                "role": "admin",
                "permissions": TIER_PERMISSIONS.get(customer_data.get("subscription_tier", "Standard").lower(), ["view"]),
                "status": "Active",
                "valid_until": customer_data.get("valid_until", ""),
                "added_date": datetime.now().isoformat().split("T")[0],
                "added_by": "admin"
            }
            
            user_access = {
                "users": [initial_user]
            }
            update_user_access(customer_id, user_access, f"Admin: Create initial user for {customer_id}")
    
    return success

def update_customer_info_admin(customer_id: str, updates: Dict) -> bool:
    """
    Update customer information
    
    Args:
        customer_id: Customer identifier
        updates: Dictionary with fields to update
    
    Returns:
        True if successful, False otherwise
    """
    info = get_customer_info(customer_id)
    if not info:
        info = {}
    
    info.update(updates)
    info["last_updated"] = datetime.now().isoformat()
    
    return update_customer_info(customer_id, info, f"Admin: Update customer info for {customer_id}")

def get_user_access_list(customer_id: str) -> List[Dict]:
    """
    Get list of users with access to a customer
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        List of user dictionaries
    """
    user_access = get_user_access(customer_id)
    if not user_access:
        return []
    
    return user_access.get("users", [])

def add_user_access(customer_id: str, email: str, tier: str, role: str = "viewer", password: str = "changeme123") -> bool:
    """
    Add user access to a customer
    
    Args:
        customer_id: Customer identifier
        email: User email address
        tier: Payment tier (Premium/Standard/Basic)
        role: User role (admin/editor/viewer)
        password: Initial password
    
    Returns:
        True if successful, False otherwise
    """
    # Validate email format
    from admin_modules.validators import validate_email
    is_valid_email, email_error = validate_email(email)
    if not is_valid_email:
        st.error(f"Invalid email: {email_error}")
        return False
    
    # Normalize email
    email = email.strip().lower()
    
    user_access = get_user_access(customer_id)
    if not user_access:
        user_access = {"users": []}
    
    # Check if user already exists
    users = user_access.get("users", [])
    for user in users:
        if user.get("email", "").lower() == email.lower():
            st.error(f"User {email} already has access to this customer")
            return False
    
    # Add new user
    new_user = {
        "email": email,
        "password": password,
        "tier": tier.lower(),
        "role": role.lower(),
        "permissions": TIER_PERMISSIONS.get(tier.lower(), ["view"]),
        "status": "Active",
        "valid_until": "",
        "added_date": datetime.now().isoformat().split("T")[0],
        "added_by": "admin"
    }
    
    users.append(new_user)
    user_access["users"] = users
    
    return update_user_access(customer_id, user_access, f"Admin: Add user {email} to {customer_id}")

def update_user_tier(customer_id: str, email: str, new_tier: str) -> bool:
    """
    Update user's payment tier
    
    Args:
        customer_id: Customer identifier
        email: User email address
        new_tier: New tier (Premium/Standard/Basic)
    
    Returns:
        True if successful, False otherwise
    """
    user_access = get_user_access(customer_id)
    if not user_access:
        return False
    
    users = user_access.get("users", [])
    updated = False
    
    for user in users:
        if user.get("email", "").lower() == email.lower():
            user["tier"] = new_tier.lower()
            user["permissions"] = TIER_PERMISSIONS.get(new_tier.lower(), ["view"])
            updated = True
            break
    
    if not updated:
        st.error(f"User {email} not found for customer {customer_id}")
        return False
    
    user_access["users"] = users
    return update_user_access(customer_id, user_access, f"Admin: Update tier to {new_tier} for {email}")

def remove_user_access(customer_id: str, email: str) -> bool:
    """
    Remove user access from a customer
    
    Args:
        customer_id: Customer identifier
        email: User email address
    
    Returns:
        True if successful, False otherwise
    """
    user_access = get_user_access(customer_id)
    if not user_access:
        return False
    
    users = user_access.get("users", [])
    original_count = len(users)
    
    users = [u for u in users if u.get("email", "").lower() != email.lower()]
    
    if len(users) == original_count:
        st.error(f"User {email} not found for customer {customer_id}")
        return False
    
    user_access["users"] = users
    return update_user_access(customer_id, user_access, f"Admin: Remove user {email} from {customer_id}")

def get_user_customers(email: str) -> List[Dict]:
    """
    Get all customers/newsletters a user has access to (reverse lookup)
    
    Args:
        email: User email address
    
    Returns:
        List of customer dictionaries with user's permissions
    """
    all_customers = list_all_customers()
    user_customers = []
    
    for customer_id in all_customers:
        user_access = get_user_access(customer_id)
        if not user_access:
            continue
        
        users = user_access.get("users", [])
        for user in users:
            if user.get("email", "").lower() == email.lower():
                # Get customer info
                info = get_customer_info(customer_id)
                branding = fetch_customer_config(customer_id, "branding")
                
                user_customers.append({
                    "customer_id": customer_id,
                    "company_name": info.get("company_name", customer_id) if info else customer_id,
                    "application_name": branding.get("application_name", customer_id) if branding else customer_id,
                    "tier": user.get("tier", "basic"),
                    "role": user.get("role", "viewer"),
                    "permissions": user.get("permissions", ["view"]),
                    "status": user.get("status", "Active")
                })
                break
    
    return user_customers

def assign_permissions_by_tier(tier: str) -> List[str]:
    """
    Get permissions list for a payment tier
    
    Args:
        tier: Payment tier (Premium/Standard/Basic)
    
    Returns:
        List of permission strings
    """
    return TIER_PERMISSIONS.get(tier.lower(), ["view"])

