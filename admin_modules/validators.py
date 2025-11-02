"""
Validation Utilities for Admin App

Centralized validation functions for forms and data inputs.
"""

import re
from typing import Tuple, Optional


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email address is required"
    
    email = email.strip().lower()
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format. Please enter a valid email address."
    
    return True, None


def validate_customer_id(customer_id: str) -> Tuple[bool, Optional[str]]:
    """
    Validate customer ID format (lowercase, alphanumeric, no spaces)
    
    Args:
        customer_id: Customer ID to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not customer_id or not customer_id.strip():
        return False, "Customer ID is required"
    
    customer_id = customer_id.strip().lower()
    
    # Check length
    if len(customer_id) < 2:
        return False, "Customer ID must be at least 2 characters"
    
    if len(customer_id) > 50:
        return False, "Customer ID must be 50 characters or less"
    
    # Check format: lowercase alphanumeric and underscores only
    if not re.match(r'^[a-z0-9_]+$', customer_id):
        return False, "Customer ID must be lowercase, alphanumeric characters and underscores only (no spaces or special characters)"
    
    # Cannot start or end with underscore
    if customer_id.startswith('_') or customer_id.endswith('_'):
        return False, "Customer ID cannot start or end with underscore"
    
    return True, None


def validate_url(url: str, field_name: str = "URL") -> Tuple[bool, Optional[str]]:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not url.strip():
        return False, f"{field_name} is required"
    
    url = url.strip()
    
    # Check if starts with http:// or https://
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, f"{field_name} must start with http:// or https://"
    
    # Basic URL validation
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    if not re.match(pattern, url):
        return False, f"Invalid {field_name} format"
    
    return True, None


def validate_required_field(value: any, field_name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that a required field is not empty
    
    Args:
        value: Field value to check
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if value is None:
        return False, f"{field_name} is required"
    
    if isinstance(value, str):
        if not value.strip():
            return False, f"{field_name} is required"
    
    if isinstance(value, list):
        if len(value) == 0:
            return False, f"{field_name} is required (at least one item needed)"
    
    return True, None


def sanitize_customer_id(customer_id: str) -> str:
    """
    Sanitize customer ID to valid format
    
    Args:
        customer_id: Customer ID to sanitize
        
    Returns:
        Sanitized customer ID (lowercase, alphanumeric, underscores)
    """
    if not customer_id:
        return ""
    
    # Convert to lowercase
    customer_id = customer_id.strip().lower()
    
    # Remove invalid characters, keep alphanumeric and underscores
    customer_id = re.sub(r'[^a-z0-9_]', '', customer_id)
    
    # Remove leading/trailing underscores
    customer_id = customer_id.strip('_')
    
    return customer_id


def validate_password(password: str, min_length: int = 8) -> Tuple[bool, Optional[str]]:
    """
    Validate password requirements
    
    Args:
        password: Password to validate
        min_length: Minimum password length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password or not password.strip():
        return False, "Password is required"
    
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"
    
    return True, None

