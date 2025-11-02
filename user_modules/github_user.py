"""
GitHub User Module

Handles all GitHub operations for the User App (GlobalNewsPilot).
Reads and writes customer configurations, newsletters, and user access files.
"""

import streamlit as st
from github import Github
from github.GithubException import GithubException
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

# Initialize GitHub client (cached in session state)
@st.cache_resource
def get_github_client():
    """Initialize and return GitHub client using Streamlit secrets"""
    try:
        # Check if secrets exist
        if not hasattr(st, 'secrets') or not st.secrets:
            st.error("⚠️ Streamlit secrets not configured. Please add secrets in Streamlit Cloud settings.")
            st.info("Required secrets: `github_token` and `github_repo`")
            return None
        
        github_token = st.secrets.get("github_token")
        if not github_token:
            st.error("⚠️ `github_token` not found in Streamlit secrets.")
            st.info("Please add your GitHub Personal Access Token in Streamlit Cloud → Settings → Secrets")
            return None
        
        return Github(github_token)
    except Exception as e:
        logger.error(f"Failed to initialize GitHub client: {e}")
        st.error(f"⚠️ Failed to connect to GitHub: {str(e)}")
        st.info("Please check that your GitHub token is valid and has 'repo' permissions.")
        return None

@st.cache_resource
def get_repo():
    """Get repository object (cached)"""
    try:
        repo_name = st.secrets.get("github_repo", "stefanhermes-code/newsletter")
        github = get_github_client()
        if not github:
            return None
        return github.get_repo(repo_name)
    except Exception as e:
        logger.error(f"Failed to get repository: {e}")
        st.error(f"Failed to access repository: {repo_name}")
        return None

def load_config(customer_id: str, config_type: str) -> Optional[Dict]:
    """
    Load configuration file from GitHub
    
    Args:
        customer_id: Customer identifier (e.g., 'htc', 'apba')
        config_type: Type of config ('branding', 'keywords', 'feeds')
    
    Returns:
        Dictionary with config data, or None if error
    """
    try:
        repo = get_repo()
        if not repo:
            return None
        
        config_path = f"customers/{customer_id}/config/{config_type}.json"
        
        try:
            file = repo.get_contents(config_path)
            content = file.decoded_content.decode('utf-8')
            return json.loads(content)
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"Config file not found: {config_path}")
                # Auto-create missing config files with default empty values
                default_configs = {
                    "keywords": {"keywords": [], "last_updated": "system", "updated_at": datetime.now().isoformat()},
                    "feeds": {"feeds": [], "last_updated": "system", "updated_at": datetime.now().isoformat()},
                    "branding": {
                        "application_name": "",
                        "newsletter_title_template": "{name} - Week {week}",
                        "footer_text": "",
                        "footer_url": "",
                        "footer_url_display": ""
                    }
                }
                
                if config_type in default_configs:
                    logger.info(f"Auto-creating missing {config_type}.json for {customer_id}")
                    default_data = default_configs[config_type]
                    # Use save_config_auto to create the file (defined later in this module)
                    if save_config_auto(customer_id, config_type, default_data, f"Auto-create missing {config_type} config"):
                        # Return the default data
                        return default_data
                    else:
                        # If save failed, still return default so app doesn't crash
                        logger.error(f"Failed to auto-create {config_type}.json, returning default")
                        return default_data
                
                return None
            raise
    
    except Exception as e:
        logger.error(f"Error loading config {config_type} for {customer_id}: {e}")
        st.error(f"Failed to load configuration: {config_type}")
        return None

def save_config_auto(customer_id: str, config_type: str, data: Dict, commit_message: Optional[str] = None) -> bool:
    """
    Automatically save configuration to GitHub (background save, invisible to user)
    
    Args:
        customer_id: Customer identifier
        config_type: Type of config ('branding', 'keywords', 'feeds')
        data: Configuration data dictionary
        commit_message: Optional custom commit message
    
    Returns:
        True if successful, False otherwise
    """
    try:
        repo = get_repo()
        if not repo:
            return False
        
        config_path = f"customers/{customer_id}/config/{config_type}.json"
        
        # Prepare content
        content = json.dumps(data, indent=2, ensure_ascii=False)
        
        # Default commit message
        if not commit_message:
            commit_message = f"Auto-save {config_type} config for {customer_id}"
        
        # Check if file exists
        try:
            file = repo.get_contents(config_path)
            # Update existing file
            repo.update_file(
                config_path,
                commit_message,
                content,
                file.sha
            )
        except GithubException as e:
            if e.status == 404:
                # File doesn't exist, create it
                # First ensure directory structure exists (create path if needed)
                repo.create_file(
                    config_path,
                    commit_message,
                    content
                )
            else:
                raise
        
        logger.info(f"Config saved: {config_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving config {config_type} for {customer_id}: {e}")
        # Don't show error to user (background save)
        return False

def load_user_access(customer_id: str) -> Optional[Dict]:
    """
    Load user access file for a customer
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Dictionary with user access data, or None if error/not found
    """
    try:
        repo = get_repo()
        if not repo:
            return None
        
        access_path = f"customers/{customer_id}/user_access.json"
        
        try:
            file = repo.get_contents(access_path)
            content = file.decoded_content.decode('utf-8')
            return json.loads(content)
        except GithubException as e:
            if e.status == 404:
                # No user access file yet - return empty structure
                return {"users": []}
            raise
    
    except Exception as e:
        logger.error(f"Error loading user access for {customer_id}: {e}")
        return None

def get_all_user_access_files() -> List[Dict]:
    """
    Scan all customers and return all user_access.json files
    
    Returns:
        List of dictionaries with customer_id and user_access data:
        [{"customer_id": "htc", "user_access": {...}}, ...]
    """
    try:
        repo = get_repo()
        if not repo:
            return []
        
        all_access = []
        
        try:
            # Get customers directory
            customers_dir = repo.get_contents("customers")
            
            if isinstance(customers_dir, list):
                # Iterate through customer folders
                for customer_folder in customers_dir:
                    if customer_folder.type == "dir":
                        customer_id = customer_folder.name
                        
                        # Try to get user_access.json
                        try:
                            access_file = repo.get_contents(
                                f"customers/{customer_id}/user_access.json"
                            )
                            content = access_file.decoded_content.decode('utf-8')
                            user_access = json.loads(content)
                            
                            all_access.append({
                                "customer_id": customer_id,
                                "user_access": user_access
                            })
                        except GithubException:
                            # No user_access.json for this customer, skip
                            continue
            else:
                # Single directory (unlikely but handle it)
                customer_id = customers_dir.name
                access_data = load_user_access(customer_id)
                if access_data:
                    all_access.append({
                        "customer_id": customer_id,
                        "user_access": access_data
                    })
        
        except GithubException as e:
            if e.status == 404:
                # No customers folder yet
                logger.info("No customers folder found in repository")
                return []
            raise
        
        return all_access
    
    except Exception as e:
        logger.error(f"Error scanning user access files: {e}")
        return []

def save_newsletter(customer_id: str, newsletter_html: str, filename: str, commit_message: Optional[str] = None) -> bool:
    """
    Save newsletter HTML to GitHub
    
    Args:
        customer_id: Customer identifier
        newsletter_html: HTML content of newsletter
        filename: Filename for newsletter (e.g., 'HTC_Week_05_2025.html')
        commit_message: Optional custom commit message
    
    Returns:
        True if successful, False otherwise
    """
    try:
        repo = get_repo()
        if not repo:
            return False
        
        newsletter_path = f"customers/{customer_id}/data/newsletters/{filename}"
        
        # Default commit message
        if not commit_message:
            commit_message = f"Add newsletter: {filename} for {customer_id}"
        
        # Check if file exists
        try:
            file = repo.get_contents(newsletter_path)
            # Update existing file
            repo.update_file(
                newsletter_path,
                commit_message,
                newsletter_html,
                file.sha
            )
        except GithubException as e:
            if e.status == 404:
                # File doesn't exist, create it
                repo.create_file(
                    newsletter_path,
                    commit_message,
                    newsletter_html
                )
            else:
                raise
        
        logger.info(f"Newsletter saved: {newsletter_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving newsletter for {customer_id}: {e}")
        st.error(f"Failed to save newsletter: {filename}")
        return False

def list_newsletters(customer_id: str) -> List[Dict]:
    """
    List all newsletters for a customer
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        List of newsletter metadata dictionaries
        [{"name": "...", "path": "...", "last_modified": "..."}, ...]
    """
    try:
        repo = get_repo()
        if not repo:
            return []
        
        newsletters_path = f"customers/{customer_id}/data/newsletters"
        
        try:
            contents = repo.get_contents(newsletters_path)
            newsletters = []
            
            if isinstance(contents, list):
                for file in contents:
                    if file.type == "file" and file.name.endswith('.html'):
                        newsletters.append({
                            "name": file.name,
                            "path": file.path,
                            "last_modified": file.last_modified,
                            "size": file.size,
                            "download_url": file.download_url
                        })
            
            # Sort by last_modified (newest first)
            newsletters.sort(key=lambda x: x.get("last_modified", ""), reverse=True)
            return newsletters
        
        except GithubException as e:
            if e.status == 404:
                # No newsletters folder yet
                return []
            raise
    
    except Exception as e:
        logger.error(f"Error listing newsletters for {customer_id}: {e}")
        return []

def get_newsletter_content(customer_id: str, filename: str) -> Optional[str]:
    """
    Get newsletter HTML content
    
    Args:
        customer_id: Customer identifier
        filename: Newsletter filename
    
    Returns:
        HTML content as string, or None if error
    """
    try:
        repo = get_repo()
        if not repo:
            return None
        
        newsletter_path = f"customers/{customer_id}/data/newsletters/{filename}"
        
        try:
            file = repo.get_contents(newsletter_path)
            return file.decoded_content.decode('utf-8')
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"Newsletter not found: {newsletter_path}")
                return None
            raise
    
    except Exception as e:
        logger.error(f"Error loading newsletter {filename} for {customer_id}: {e}")
        return None

