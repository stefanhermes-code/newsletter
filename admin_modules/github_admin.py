"""
GitHub Admin Module

Handles all GitHub operations for the Admin App (GNP_Admin).
Full read/write access to customer configurations, user access files, and customer data.
"""

import streamlit as st
from github import Github
from github.GithubException import GithubException
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

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

def list_all_customers() -> List[str]:
    """
    List all customer IDs from customers/ folder
    
    Returns:
        List of customer_id strings
    """
    try:
        repo = get_repo()
        if not repo:
            return []
        
        customers = []
        try:
            customers_dir = repo.get_contents("customers")
            
            if isinstance(customers_dir, list):
                for item in customers_dir:
                    if item.type == "dir":
                        customers.append(item.name)
            else:
                if customers_dir.type == "dir":
                    customers.append(customers_dir.name)
        
        except GithubException as e:
            if e.status == 404:
                # No customers folder yet
                return []
            raise
        
        return sorted(customers)
    
    except Exception as e:
        logger.error(f"Error listing customers: {e}")
        return []

def fetch_customer_config(customer_id: str, config_type: str) -> Optional[Dict]:
    """
    Fetch customer configuration file from GitHub
    
    Args:
        customer_id: Customer identifier
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
                return None
            raise
    
    except Exception as e:
        logger.error(f"Error fetching config {config_type} for {customer_id}: {e}")
        return None

def update_customer_config(customer_id: str, config_type: str, data: Dict, commit_message: Optional[str] = None) -> bool:
    """
    Update customer configuration in GitHub
    
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
            commit_message = f"Admin: Update {config_type} config for {customer_id}"
        
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
                repo.create_file(
                    config_path,
                    commit_message,
                    content
                )
            else:
                raise
        
        logger.info(f"Config updated: {config_path}")
        # Clear cache for get_repo function (if available)
        # Note: In newer Streamlit versions, cache_resource functions handle clearing differently
        try:
            if hasattr(get_repo, 'clear'):
                get_repo.clear()
            elif hasattr(get_repo, 'cache_clear'):
                get_repo.cache_clear()
        except (AttributeError, Exception) as cache_error:
            # Cache clearing failed - not critical, cache will refresh on next call
            logger.debug(f"Cache clearing not available or failed: {cache_error}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating config {config_type} for {customer_id}: {e}")
        st.error(f"Failed to update configuration: {e}")
        return False

def get_customer_info(customer_id: str) -> Optional[Dict]:
    """
    Get customer info from customer_info.json
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Dictionary with customer info, or None if error
    """
    try:
        repo = get_repo()
        if not repo:
            return None
        
        info_path = f"customers/{customer_id}/customer_info.json"
        
        try:
            file = repo.get_contents(info_path)
            content = file.decoded_content.decode('utf-8')
            return json.loads(content)
        except GithubException as e:
            if e.status == 404:
                # No customer_info.json yet
                return {}
            raise
    
    except Exception as e:
        logger.error(f"Error loading customer info for {customer_id}: {e}")
        return None

def update_customer_info(customer_id: str, info_data: Dict, commit_message: Optional[str] = None) -> bool:
    """
    Update customer_info.json
    
    Args:
        customer_id: Customer identifier
        info_data: Customer info dictionary
        commit_message: Optional custom commit message
    
    Returns:
        True if successful, False otherwise
    """
    try:
        repo = get_repo()
        if not repo:
            return False
        
        info_path = f"customers/{customer_id}/customer_info.json"
        content = json.dumps(info_data, indent=2, ensure_ascii=False)
        
        if not commit_message:
            commit_message = f"Admin: Update customer info for {customer_id}"
        
        try:
            file = repo.get_contents(info_path)
            repo.update_file(
                info_path,
                commit_message,
                content,
                file.sha
            )
        except GithubException as e:
            if e.status == 404:
                repo.create_file(
                    info_path,
                    commit_message,
                    content
                )
            else:
                raise
        
        logger.info(f"Customer info updated: {info_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating customer info for {customer_id}: {e}")
        st.error(f"Failed to update customer info: {e}")
        return False

def get_user_access(customer_id: str) -> Optional[Dict]:
    """
    Get user access file for a customer
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Dictionary with user access data, or None if error
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

def update_user_access(customer_id: str, user_access_data: Dict, commit_message: Optional[str] = None) -> bool:
    """
    Update user_access.json
    
    Args:
        customer_id: Customer identifier
        user_access_data: User access data dictionary
        commit_message: Optional custom commit message
    
    Returns:
        True if successful, False otherwise
    """
    try:
        repo = get_repo()
        if not repo:
            return False
        
        access_path = f"customers/{customer_id}/user_access.json"
        content = json.dumps(user_access_data, indent=2, ensure_ascii=False)
        
        if not commit_message:
            commit_message = f"Admin: Update user access for {customer_id}"
        
        try:
            file = repo.get_contents(access_path)
            repo.update_file(
                access_path,
                commit_message,
                content,
                file.sha
            )
        except GithubException as e:
            if e.status == 404:
                repo.create_file(
                    access_path,
                    commit_message,
                    content
                )
            else:
                raise
        
        logger.info(f"User access updated: {access_path}")
        return True
    
    except Exception as e:
        logger.error(f"Error updating user access for {customer_id}: {e}")
        st.error(f"Failed to update user access: {e}")
        return False

def create_customer_folder(customer_id: str) -> bool:
    """
    Create customer folder structure in GitHub
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        True if successful, False otherwise
    """
    try:
        repo = get_repo()
        if not repo:
            return False
        
        # Create folder structure by creating placeholder files
        # GitHub doesn't support empty folders, so we create README files
        folders_to_create = [
            f"customers/{customer_id}",
            f"customers/{customer_id}/config",
            f"customers/{customer_id}/data",
            f"customers/{customer_id}/data/newsletters"
        ]
        
        for folder in folders_to_create:
            readme_path = f"{folder}/README.md"
            try:
                # Try to get existing file
                repo.get_contents(readme_path)
                # File exists, skip
            except GithubException as e:
                if e.status == 404:
                    # Create README to establish folder structure
                    repo.create_file(
                        readme_path,
                        f"Create folder structure for {customer_id}",
                        f"# {folder}\n\nThis folder contains data for customer: {customer_id}\n"
                    )
        
        logger.info(f"Customer folder structure created: {customer_id}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating customer folder for {customer_id}: {e}")
        st.error(f"Failed to create customer folder: {e}")
        return False

def list_customer_files(customer_id: str, folder_path: str = "") -> List[Dict]:
    """
    List files in a customer's folder
    
    Args:
        customer_id: Customer identifier
        folder_path: Subfolder path (e.g., "data/newsletters")
    
    Returns:
        List of file dictionaries with name, path, size, etc.
    """
    try:
        repo = get_repo()
        if not repo:
            return []
        
        if folder_path:
            full_path = f"customers/{customer_id}/{folder_path}"
        else:
            full_path = f"customers/{customer_id}"
        
        try:
            contents = repo.get_contents(full_path)
            files = []
            
            if isinstance(contents, list):
                for item in contents:
                    files.append({
                        "name": item.name,
                        "path": item.path,
                        "type": item.type,
                        "size": item.size,
                        "sha": item.sha,
                        "download_url": item.download_url,
                        "last_modified": item.last_modified if hasattr(item, 'last_modified') else None
                    })
            
            return files
        
        except GithubException as e:
            if e.status == 404:
                return []
            raise
    
    except Exception as e:
        logger.error(f"Error listing files for {customer_id}: {e}")
        return []

def get_file_content(customer_id: str, file_path: str) -> Optional[str]:
    """
    Get file content from GitHub
    
    Args:
        customer_id: Customer identifier
        file_path: Path relative to customer folder (e.g., "data/newsletters/file.html")
    
    Returns:
        File content as string, or None if error
    """
    try:
        repo = get_repo()
        if not repo:
            return None
        
        full_path = f"customers/{customer_id}/{file_path}"
        
        try:
            file = repo.get_contents(full_path)
            return file.decoded_content.decode('utf-8')
        except GithubException as e:
            if e.status == 404:
                logger.warning(f"File not found: {full_path}")
                return None
            raise
    
    except Exception as e:
        logger.error(f"Error getting file content for {customer_id}/{file_path}: {e}")
        return None

def get_commit_history(customer_id: str, file_path: Optional[str] = None, limit: int = 20) -> List[Dict]:
    """
    Get commit history for a customer or specific file
    
    Args:
        customer_id: Customer identifier
        file_path: Optional specific file path (relative to customer folder)
        limit: Maximum number of commits to return
    
    Returns:
        List of commit dictionaries
    """
    try:
        repo = get_repo()
        if not repo:
            return []
        
        if file_path:
            full_path = f"customers/{customer_id}/{file_path}"
        else:
            full_path = f"customers/{customer_id}"
        
        commits = repo.get_commits(path=full_path)
        
        history = []
        for commit in commits[:limit]:
            history.append({
                "sha": commit.sha,
                "message": commit.commit.message,
                "author": commit.commit.author.name,
                "date": commit.commit.author.date.isoformat() if commit.commit.author.date else None,
                "url": commit.html_url
            })
        
        return history
    
    except Exception as e:
        logger.error(f"Error getting commit history for {customer_id}: {e}")
        return []

