# Newsletter Tool Cloud Migration - Implementation Plan

**Related Document:** [Design Document](./Newsletter%20Tool%20Cloud%20Migration%20-%20DESIGN%20DOCUMENT.md)

This document provides detailed implementation specifications, function mappings, and code structure for developing the Newsletter Tool Cloud applications.

---

## Admin App Implementation - Function Mapping

This section maps all design requirements (from the Design Document) to specific functions/modules that need to be implemented in the Admin App.

### Admin App Module Structure:

```
admin_modules/
├── __init__.py
├── customer_manager.py          # Customer CRUD operations
├── email_sender.py              # Email sending functionality (SMTP/API)
├── onboarding_manager.py        # Onboarding initiation & review
├── onboarding_wizard.py         # Manual entry wizard (fallback)
├── config_viewer.py             # View/edit customer configs
├── activity_monitor.py           # Monitor customer activities
├── analytics_engine.py          # Cross-customer analytics
├── export_import.py            # Excel export/import
└── github_admin.py              # GitHub operations for admin

# Note: Onboarding is now integrated into Admin App (GNP_Admin)
# No separate onboarding_app needed
```

### Function Mapping by Feature:

#### **1. Customer Management**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Customer List View | `customer_manager.py` | `list_all_customers()`, `get_customer_list()` |
| Customer Details | `customer_manager.py` | `get_customer_details(customer_id)` |
| Search/Filter Customers | `customer_manager.py` | `search_customers(query)`, `filter_customers(status)` |
| Edit Customer Info | `customer_manager.py` | `update_customer_info(customer_id, data)` |
| Activate/Deactivate | `customer_manager.py` | `set_customer_status(customer_id, status)` |
| Delete Customer | `customer_manager.py` | `delete_customer(customer_id)` |
| Bulk Actions | `customer_manager.py` | `bulk_update_status(customer_ids, status)` |
| **Manage User Access** | `customer_manager.py` | `get_user_access(customer_id)`, `add_user_access(customer_id, email, tier, role)`, `update_user_tier(customer_id, email, new_tier)`, `remove_user_access(customer_id, email)` |
| **View User's Customers** | `customer_manager.py` | `get_user_customers(email)` - Returns all newsletters user has access to with permissions |

#### **2. Customer Onboarding**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| **Admin: Initiate Onboarding** | `onboarding_manager.py` | `initiate_onboarding(customer_email, customer_name)` |
| **Admin: Generate Onboarding Token** | `onboarding_manager.py` | `generate_onboarding_token(email)` |
| **Admin: Send Onboarding Email** | `email_sender.py` | `send_onboarding_email(email, token, link)` |
| **Admin: View Pending Submissions** | `onboarding_manager.py` | `get_pending_submissions()` |
| **Admin: Review Submission** | `onboarding_manager.py` | `get_submission_details(token)` |
| **Admin: Approve Submission** | `onboarding_manager.py` | `approve_submission(token, customer_id)` |
| **Admin: Edit Submission** | `onboarding_manager.py` | `edit_submission(token, changes)` |
| **Customer: Load Onboarding Form** | `streamlit_onboarding_app.py` | `load_onboarding_form(token)` |
| **Customer: Validate Token** | `onboarding_manager.py` | `validate_onboarding_token(token)` |
| **Customer: Save Progress** | `onboarding_manager.py` | `save_onboarding_progress(token, step_data)` |
| **Customer: Submit Form** | `onboarding_manager.py` | `submit_onboarding_form(token, form_data)` |
| **Admin: Manual Entry Wizard** | `onboarding_wizard.py` | `render_manual_wizard()` |
| Create Config Files | `onboarding_manager.py` | `create_customer_configs(customer_id, data)` |
| Generate Secrets Template | `onboarding_manager.py` | `generate_secrets_template(customer_id)` |
| Generate Welcome Email | `email_sender.py` | `send_welcome_email(customer_id, app_url)` |
| Test Email Connection | `email_sender.py` | `test_email_connection()` |
| Create Customer Record | `customer_manager.py` | `create_customer_record(customer_data)` |

#### **3. Configuration Viewer**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Load Customer Configs | `config_viewer.py` | `load_customer_configs(customer_id)` |
| View Keywords | `config_viewer.py` | `get_keywords(customer_id)` |
| Edit Keywords | `config_viewer.py` | `update_keywords(customer_id, keywords)` |
| View Feeds | `config_viewer.py` | `get_feeds(customer_id)` |
| Edit Feeds | `config_viewer.py` | `update_feeds(customer_id, feeds)` |
| View Branding | `config_viewer.py` | `get_branding(customer_id)` |
| Edit Branding | `config_viewer.py` | `update_branding(customer_id, branding)` |
| View Config History | `github_admin.py` | `get_config_history(customer_id, file_path)` |
| Compare Config Versions | `github_admin.py` | `compare_config_versions(customer_id, file_path, commit1, commit2)` |
| Rollback Config | `github_admin.py` | `rollback_config(customer_id, file_path, commit)` |

#### **4. Activity Monitor**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| List All Newsletters | `activity_monitor.py` | `list_all_newsletters(customer_id=None)` |
| Get Customer Newsletters | `activity_monitor.py` | `get_customer_newsletters(customer_id)` |
| Download Newsletter | `github_admin.py` | `download_file(customer_id, file_path)` |
| List Newsletters | `activity_monitor.py` | `list_newsletters(customer_id)` |
| View Database Activity | `activity_monitor.py` | `get_database_activity(customer_id)` |
| Get Usage Statistics | `activity_monitor.py` | `get_usage_stats(customer_id)` |
| Activity Timeline | `activity_monitor.py` | `get_activity_timeline(customer_id)` |

#### **5. Analytics**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Popular Keywords | `analytics_engine.py` | `get_popular_keywords(limit=10)` |
| Popular Feeds | `analytics_engine.py` | `get_popular_feeds(limit=10)` |
| Most Active Customers | `analytics_engine.py` | `get_most_active_customers(days=30)` |
| Keyword Trends | `analytics_engine.py` | `get_keyword_trends(keyword, days=90)` |
| Feed Trends | `analytics_engine.py` | `get_feed_trends(feed_url, days=90)` |
| Newsletter Trends | `analytics_engine.py` | `get_newsletter_trends(days=90)` |
| Customer Retention | `analytics_engine.py` | `calculate_retention_rate()` |
| Engagement Metrics | `analytics_engine.py` | `get_engagement_metrics(customer_id)` |

#### **6. Export/Import**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Export All Configs to Excel | `export_import.py` | `export_all_configs_to_excel(output_path)` |
| Export Customer Configs | `export_import.py` | `export_customer_configs(customer_id, output_path)` |
| Import Configs from Excel | `export_import.py` | `import_configs_from_excel(file_path, customer_id)` |
| Export Analytics Data | `export_import.py` | `export_analytics_to_excel(output_path)` |
| Bulk Update Configs | `export_import.py` | `bulk_update_from_excel(file_path)` |

#### **7. GitHub Operations (Admin)**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Fetch Customer Config | `github_admin.py` | `fetch_customer_config(customer_id, config_type)` |
| Update Customer Config | `github_admin.py` | `update_customer_config(customer_id, config_type, data, commit_message)` |
| List Customer Files | `github_admin.py` | `list_customer_files(customer_id, folder_path)` |
| Get File Content | `github_admin.py` | `get_file_content(customer_id, file_path)` |
| Create Customer Folder | `github_admin.py` | `create_customer_folder(customer_id)` |
| Get Commit History | `github_admin.py` | `get_commit_history(customer_id, file_path)` |

---

## Admin App Main Entry Point Structure:

```python
# streamlit_admin_app.py structure

import streamlit as st
from admin_modules import (
    customer_manager,
    onboarding_wizard,
    config_viewer,
    activity_monitor,
    analytics_engine,
    export_import
)

def main():
    st.set_page_config(page_title="Newsletter Tool Admin", layout="wide")
    
    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Overview", "Customer Management", "Onboarding", "Configuration", "Activity", "Analytics", "Export/Import"]
    )
    
    if page == "Overview":
        render_overview_dashboard()
    elif page == "Customer Management":
        render_customer_management()
    elif page == "Onboarding":
        onboarding_wizard.render_wizard()
    elif page == "Configuration":
        config_viewer.render_config_viewer()
    elif page == "Activity":
        activity_monitor.render_activity_monitor()
    elif page == "Analytics":
        analytics_engine.render_analytics()
    elif page == "Export/Import":
        export_import.render_export_import()

if __name__ == "__main__":
    main()
```

---

## Implementation Checklist:

### Customer Manager Module (`admin_modules/customer_manager.py`)
- [ ] `list_all_customers()` - Load customer list from `customers/` folder in `stefanhermes-code/newsletter` repo
- [ ] `get_customer_details(customer_id)` - Load `customers/{customer_id}/customer_info.json` and config files
- [ ] `create_customer_record()` - Create `customers/{customer_id}/customer_info.json` in GitHub
- [ ] `update_customer_info()` - Update `customers/{customer_id}/customer_info.json` in GitHub
- [ ] `delete_customer()` - Archive or delete customer folder from GitHub
- [ ] `search_customers(query)` - Search by company name, ID, email
- [ ] `filter_customers(status)` - Filter by active/inactive status
- [ ] `set_customer_status(customer_id, status)` - Update status in customer_info.json
- [ ] `bulk_update_status(customer_ids, status)` - Bulk status updates
- [ ] `get_user_access(customer_id)` - Get list of users from `customers/{customer_id}/user_access.json`
- [ ] `add_user_access(customer_id, email, tier, role)` - Add user with tier (Premium/Standard/Basic) and role to `user_access.json`
- [ ] `update_user_tier(customer_id, email, new_tier)` - Upgrade/downgrade user tier in `user_access.json`
- [ ] `get_user_permissions(customer_id, email)` - Get user's permissions from `customers/{customer_id}/user_access.json`
- [ ] `remove_user_access(customer_id, email)` - Remove user from `user_access.json`
- [ ] `get_user_customers(email)` - Scan all `customers/*/user_access.json` files to find all newsletters user has access to (reverse lookup)
- [ ] `assign_permissions_by_tier(tier)` - Auto-assign permissions based on payment tier
- [ ] Integration with `github_admin.py` to read/write files in `stefanhermes-code/newsletter` repository

### Email Sender Module (`admin_modules/email_sender.py`)
- [ ] `send_onboarding_email(email, token, link)` - Send onboarding invitation
- [ ] `send_welcome_email(customer_id, app_url)` - Send welcome email
- [ ] `send_submission_notification(admin_email, customer_email)` - Notify admin
- [ ] `test_email_connection()` - Verify email setup works
- [ ] Support for SMTP (smtplib) and third-party services (SendGrid, Mailgun, AWS SES)
- [ ] Fallback: Return link for manual sending if email fails
- [ ] Load email config from Streamlit secrets

### Onboarding Manager Module (`admin_modules/onboarding_manager.py`)
- [ ] `initiate_onboarding(customer_email, customer_name)` - Start process
- [ ] `generate_onboarding_token(email)` - Create unique token
- [ ] `send_onboarding_email(email, token, link)` - Send invitation email (calls email_sender)
- [ ] `validate_onboarding_token(token)` - Verify token validity
- [ ] `get_pending_submissions()` - List all pending customer submissions
- [ ] `get_submission_details(token)` - Load customer submission
- [ ] `approve_submission(token, customer_id)` - Approve and create account
- [ ] `edit_submission(token, changes)` - Modify before approval
- [ ] `save_onboarding_progress(token, step_data)` - Auto-save customer progress
- [ ] `submit_onboarding_form(token, form_data)` - Customer submission handler
- [ ] `create_customer_configs(customer_id, data)` - Generate all config files in `customers/{customer_id}/config/` in `stefanhermes-code/newsletter`
- [ ] `generate_secrets_template(customer_id)` - Output TOML template for Streamlit Cloud deployment
- [ ] `generate_welcome_email(customer_id, app_url)` - Email template
- [ ] Integration with `customer_manager.create_customer_record()` and `github_admin.py` to commit files to `stefanhermes-code/newsletter`

### Onboarding App (Separate Streamlit App) (`onboarding_app/streamlit_onboarding_app.py`)
- [ ] Token validation from URL parameter
- [ ] Multi-step form (7 steps, customer-friendly language)
- [ ] Auto-save progress functionality
- [ ] Navigation (back/forward between steps)
- [ ] Form validation
- [ ] Submit to admin dashboard
- [ ] Confirmation page after submission
- [ ] Integration with `onboarding_manager` for save/submit

### Onboarding Storage (`onboarding_app/onboarding_storage.py`)
- [ ] Store onboarding submissions (JSON or database)
- [ ] Retrieve submissions by token
- [ ] Update submission status
- [ ] Clean up expired tokens

### Manual Entry Wizard Module (`admin_modules/onboarding_wizard.py`) - Fallback
- [ ] Multi-step Streamlit form with navigation
- [ ] `validate_customer_id(customer_id)` - Check uniqueness
- [ ] `collect_basic_info()` - Step 1 form
- [ ] `collect_branding_info()` - Step 2 form
- [ ] `collect_keywords()` - Step 3 form (with import option)
- [ ] `collect_feeds()` - Step 4 form (with URL testing)
- [ ] `collect_deployment_config()` - Step 5 form
- [ ] `review_and_validate(form_data)` - Validation before creation
- [ ] Integration with `onboarding_manager` for config creation

### Config Viewer Module (`admin_modules/config_viewer.py`)
- [ ] `load_customer_configs(customer_id)` - Load all configs from `customers/{customer_id}/config/` in `stefanhermes-code/newsletter`
- [ ] `get_keywords(customer_id)` - Fetch `customers/{customer_id}/config/keywords.json`
- [ ] `update_keywords(customer_id, keywords)` - Save to `customers/{customer_id}/config/keywords.json` in GitHub
- [ ] `get_feeds(customer_id)` - Fetch `customers/{customer_id}/config/feeds.json`
- [ ] `update_feeds(customer_id, feeds)` - Save to `customers/{customer_id}/config/feeds.json` in GitHub
- [ ] `get_branding(customer_id)` - Fetch `customers/{customer_id}/config/branding.json`
- [ ] `update_branding(customer_id, branding)` - Save to `customers/{customer_id}/config/branding.json` in GitHub
- [ ] Streamlit UI for inline editing (using `st.data_editor` or custom forms)
- [ ] Integration with `github_admin.py` for commit history

### Activity Monitor Module (`admin_modules/activity_monitor.py`)
- [ ] `list_all_newsletters(customer_id=None)` - List all newsletters from `customers/{customer_id}/data/newsletters/` in `stefanhermes-code/newsletter`
- [ ] `get_customer_newsletters(customer_id)` - Customer-specific list from `customers/{customer_id}/data/newsletters/`
- [ ] `list_newsletters(customer_id)` - List all newsletters created for customer
- [ ] `get_database_activity(customer_id)` - Database stats and info
- [ ] `get_usage_stats(customer_id)` - Usage metrics
- [ ] `get_activity_timeline(customer_id)` - Chronological activity view
- [ ] File preview functionality
- [ ] Integration with `github_admin.py` for file downloads

### Analytics Engine Module (`admin_modules/analytics_engine.py`)
- [ ] `get_popular_keywords(limit=10)` - Aggregate across all customers
- [ ] `get_popular_feeds(limit=10)` - Aggregate across all customers
- [ ] `get_most_active_customers(days=30)` - Sort by activity
- [ ] `get_keyword_trends(keyword, days=90)` - Time series analysis
- [ ] `get_feed_trends(feed_url, days=90)` - Time series analysis
- [ ] `get_newsletter_trends(days=90)` - Generation trends
- [ ] `calculate_retention_rate()` - Customer retention metrics
- [ ] `get_engagement_metrics(customer_id)` - Per-customer engagement
- [ ] Visualization functions using Streamlit charts

### Export/Import Module (`admin_modules/export_import.py`)
- [ ] `export_all_configs_to_excel(output_path)` - Multi-sheet workbook
- [ ] `export_customer_configs(customer_id, output_path)` - Single customer
- [ ] `import_configs_from_excel(file_path, customer_id)` - Parse and validate
- [ ] `export_analytics_to_excel(output_path)` - Analytics data export
- [ ] `bulk_update_from_excel(file_path)` - Bulk operations
- [ ] Excel template generation
- [ ] Validation and error handling

### GitHub Admin Module (`admin_modules/github_admin.py`)
- [ ] GitHub API client initialization (admin token from Streamlit secrets)
  - Repository: `stefanhermes-code/newsletter`
  - Load from secrets: `st.secrets["github_token"]` and `st.secrets["github_repo"]`
- [ ] `fetch_customer_config(customer_id, config_type)` - Read JSON files from `customers/{customer_id}/config/{config_type}.json`
- [ ] `update_customer_config(customer_id, config_type, data, commit_message)` - Write JSON files to GitHub
- [ ] `list_customer_files(customer_id, folder_path)` - List files in folder (e.g., `customers/{customer_id}/data/newsletters/`)
- [ ] `get_file_content(customer_id, file_path)` - Read file content from GitHub
- [ ] `create_customer_folder(customer_id)` - Create folder structure: `customers/{customer_id}/config/`, `customers/{customer_id}/data/`
- [ ] `get_commit_history(customer_id, file_path)` - Git commit history for file
- [ ] `compare_config_versions(...)` - Diff between commits
- [ ] `rollback_config(...)` - Revert to previous version
- [ ] `download_file(customer_id, file_path)` - Download file content
- [ ] Error handling and rate limit management (5000 requests/hour for authenticated)

---

## User App Implementation

### User App Module Structure:

```
user_modules/
├── __init__.py
├── customer_selector.py        # Newsletter selector & user access management
├── news_finder.py              # Google News + RSS finding (background)
├── article_dashboard.py         # Article display with preview
├── newsletter_generator.py     # Direct newsletter generation (no draft step)
├── config_manager.py           # User config editing (keywords/feeds)
└── github_user.py              # GitHub operations (read/write configs)
```

### Function Mapping by Feature:

#### **1. News Finding**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Find News (Google) | `news_finder.py` | `find_news_google(keywords, time_period)` |
| Find News (RSS) | `news_finder.py` | `find_news_rss(feed_urls, time_period)` |
| Background Processing | `news_finder.py` | `find_news_background(keywords, feeds, time_period)` |
| Status Indicator | `article_dashboard.py` | `show_finding_status()` |

#### **2. Article Dashboard**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Display Articles | `article_dashboard.py` | `display_articles(articles)` |
| **Article Preview** | `article_dashboard.py` | `preview_article(article_url)` |
| Filter Articles | `article_dashboard.py` | `filter_articles(articles, category, keyword)` |
| Select Articles | `article_dashboard.py` | `select_articles(article_ids)` |
| Show Selected Summary | `article_dashboard.py` | `show_selected_summary(selected_articles)` |

#### **3. Newsletter Generation**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Generate Newsletter | `newsletter_generator.py` | `generate_newsletter(selected_articles, branding)` |
| Format HTML | `newsletter_generator.py` | `format_html_newsletter(articles, branding)` |
| Mark Articles Used | `newsletter_generator.py` | `mark_articles_used(article_ids)` |
| Save Newsletter | `github_user.py` | `save_newsletter(newsletter_html, filename)` |
| Download Newsletter | `newsletter_generator.py` | `download_newsletter(newsletter_html)` |

**Note:** No draft generation function needed - direct newsletter creation only.

#### **4. Configuration Management**

| Design Requirement | Function/Module | Function Name |
|-------------------|-----------------|---------------|
| Load Keywords | `config_manager.py` | `load_keywords()` |
| Edit Keywords | `config_manager.py` | `edit_keywords(keywords)` |
| Load Feeds | `config_manager.py` | `load_feeds()` |
| Edit Feeds | `config_manager.py` | `edit_feeds(feeds)` |
| **Background Save** | `github_user.py` | `save_config_auto(config_type, data)` |
| Validation | `config_manager.py` | `validate_config(config_type, data)` |

**Note:** Saving happens automatically in background - no user-visible save button needed.

### User App Main Entry Point Structure:

```python
# streamlit_user_app.py structure

import streamlit as st
from user_modules.customer_selector import (
    get_user_email, 
    get_user_newsletters, 
    render_newsletter_selector, 
    set_current_customer,
    get_current_customer,
    load_customer_config
)
from user_modules import (
    news_finder,
    article_dashboard,
    newsletter_generator,
    config_manager
)

# Initialize session state
if 'user_email' not in st.session_state:
    st.session_state.user_email = get_user_email()  # From input or auth
    
if 'current_customer_id' not in st.session_state:
    st.session_state.current_customer_id = None

# Get user's accessible newsletters
user_newsletters = get_user_newsletters(st.session_state.user_email)

# Newsletter selector (always visible in sidebar or header)
if not st.session_state.current_customer_id:
    # User must select newsletter first
    st.title("Select Your Newsletter")
    selected_newsletter = render_newsletter_selector(user_newsletters)
    if selected_newsletter:
        set_current_customer(selected_newsletter['customer_id'])
        st.rerun()
else:
    # Load current customer config
    current_customer = get_current_customer()
    customer_config = load_customer_config(st.session_state.current_customer_id)
    
    # Set page title with customer branding
    st.set_page_config(
        page_title=customer_config['branding']['application_name'], 
        layout="wide"
    )
    
    # Newsletter switcher in sidebar
    st.sidebar.title("Newsletter")
    newsletter_list = [n['name'] for n in user_newsletters]
    current_index = next((i for i, n in enumerate(user_newsletters) 
                         if n['customer_id'] == st.session_state.current_customer_id), 0)
    selected_newsletter_name = st.sidebar.selectbox(
        "Switch Newsletter",
        newsletter_list,
        index=current_index
    )
    if selected_newsletter_name != user_newsletters[current_index]['name']:
        new_customer_id = next(n['customer_id'] for n in user_newsletters 
                               if n['name'] == selected_newsletter_name)
        set_current_customer(new_customer_id)
        st.rerun()
    
    # Main navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Dashboard", "Newsletters", "Configuration"]
    )
    
    # Permission-based navigation (hide tabs user can't access)
    available_pages = ["Dashboard", "Newsletters"]
    if has_permission("edit_config"):
        available_pages.append("Configuration")
    
    page = st.sidebar.selectbox("Navigation", available_pages)
    
    if page == "Dashboard":
        render_dashboard(customer_config, user_permissions)  # News finding + article selection + newsletter generation
    elif page == "Newsletters":
        render_newsletters_viewer(st.session_state.current_customer_id, user_permissions)
    elif page == "Configuration":
        if has_permission("edit_config"):
            config_manager.render_config_editor(st.session_state.current_customer_id, user_permissions)
        else:
            st.error("You don't have permission to edit configuration. Premium tier required.")

def render_dashboard(customer_config):
    # All operations use st.session_state.current_customer_id
    # Load keywords/feeds for current customer
    # ...
    
if __name__ == "__main__":
    main()
```

### Implementation Checklist:

- [ ] **News Finder Module (`user_modules/news_finder.py`)**
  - [ ] `find_news_google(keywords, time_period)` - Google News API/search
  - [ ] `find_news_rss(feed_urls, time_period)` - RSS feed parsing
  - [ ] `find_news_background(...)` - Combined search with status updates
  - [ ] Categorization based on keywords
  - [ ] Duplicate detection

- [ ] **Article Dashboard Module (`user_modules/article_dashboard.py`)**
  - [ ] `display_articles(articles)` - Article list display
  - [ ] `preview_article(article_url)` - **Article preview functionality**
  - [ ] `filter_articles(...)` - Filtering and search
  - [ ] `select_articles(article_ids)` - Selection interface
  - [ ] `show_selected_summary(...)` - Selected articles panel

- [ ] **Newsletter Generator Module (`user_modules/newsletter_generator.py`)**
  - [ ] `generate_newsletter(selected_articles, branding)` - Direct generation
  - [ ] `format_html_newsletter(...)` - HTML formatting with branding
  - [ ] `mark_articles_used(article_ids)` - Update database
  - [ ] `download_newsletter(...)` - Download functionality
  - [ ] Integration with `github_user.py` for saving

- [ ] **Customer Selector Module (`user_modules/customer_selector.py`)**
  - [ ] `get_user_email()` - Get from input/session/auth
  - [ ] `get_user_newsletters(user_email)` - Scan all customers' `user_access.json`, return newsletters with permissions/tiers
  - [ ] `get_user_permissions(user_email, customer_id)` - Get user's tier/permissions for specific newsletter
  - [ ] `render_newsletter_selector(user_newsletters, current_customer_id)` - **Always visible in sidebar** (not just at startup)
  - [ ] `switch_newsletter(customer_id)` - Switch newsletter during app usage (available throughout)
  - [ ] `load_customer_config(customer_id)` - Load `customers/{customer_id}/config/branding.json` for selected customer
  - [ ] `set_current_customer(customer_id)` - Store in session state
  - [ ] `get_current_customer()` - Retrieve from session state
  - [ ] `has_permission(permission_name)` - Check if user has permission for current newsletter (e.g., "edit_config", "generate")
  - [ ] Integration with `github_user.py` to read `user_access.json` from all customers in `stefanhermes-code/newsletter`
  - [ ] Handle user with no access (show message)
  - [ ] Permission-based UI rendering (hide/show features based on tier)

- [ ] **Config Manager Module (`user_modules/config_manager.py`)**
  - [ ] `load_keywords(customer_id)` - Load from `customers/{customer_id}/config/keywords.json` in `stefanhermes-code/newsletter`
  - [ ] `edit_keywords(keywords, customer_id)` - Edit interface (only if user has `edit_config` permission)
  - [ ] `load_feeds(customer_id)` - Load from `customers/{customer_id}/config/feeds.json`
  - [ ] `edit_feeds(feeds, customer_id)` - Edit interface (only if user has `edit_config` permission)
  - [ ] `validate_config(...)` - Validation before save
  - [ ] Integration with `github_user.py` for background saving to `stefanhermes-code/newsletter`

- [ ] **GitHub User Module (`user_modules/github_user.py`)**
  - [ ] GitHub API client initialization
    - Repository: `stefanhermes-code/newsletter`
    - Load from Streamlit secrets: `st.secrets["github_token"]` and `st.secrets["github_repo"]`
  - [ ] `save_config_auto(config_type, data)` - Automatic background save to `customers/{customer_id}/config/{config_type}.json`
  - [ ] `save_newsletter(newsletter_html, filename)` - Save newsletter to `customers/{customer_id}/data/newsletters/{filename}`
  - [ ] `load_config(config_type)` - Load configs from GitHub `customers/{customer_id}/config/{config_type}.json`
  - [ ] `load_user_access(customer_id)` - Load `customers/{customer_id}/user_access.json` to check permissions
  - [ ] `get_all_user_access_files()` - Scan all `customers/*/user_access.json` to find user's newsletters
  - [ ] Error handling for network issues

---

## Development Phases

### Phase 1: Foundation
1. Set up GitHub repository structure in `stefanhermes-code/newsletter`
   - Create folder structure: `admin_modules/`, `user_modules/`, `onboarding_app/`, `config/`
   - Initialize `customers/` folder for customer-specific data
   - Set up `.gitignore`, `requirements.txt`, `README.md`
2. Implement `github_admin.py` (core GitHub operations)
   - Connect to `stefanhermes-code/newsletter` repository
   - Test read/write operations
3. Implement `customer_manager.py` (basic CRUD)
4. Create admin app skeleton with navigation

### Phase 2: Onboarding
1. Implement `onboarding_wizard.py` (all 7 steps)
2. Integration testing with GitHub
3. Test config file creation

### Phase 3: Configuration Management
1. Implement `config_viewer.py`
2. Add history and rollback features
3. Test read/write operations

### Phase 4: Monitoring & Analytics
1. Implement `activity_monitor.py`
2. Implement `analytics_engine.py`
3. Add visualizations

### Phase 5: Export/Import
1. Implement `export_import.py`
2. Test Excel round-trip
3. Validate data integrity

### Phase 6: Integration & Testing
1. End-to-end testing
2. User acceptance testing
3. Performance optimization
4. Documentation

---

## Technical Notes

### Dependencies Required:
- `streamlit` - UI framework
- `PyGithub` or `github3.py` - GitHub API client
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `python-dateutil` - Date parsing
- `json` - Config file handling

### GitHub API Considerations:
- **Repository:** `stefanhermes-code/newsletter`
- Rate limits: 5000 requests/hour for authenticated requests
- Repository structure:
  ```
  stefanhermes-code/newsletter/
  ├── admin_modules/
  ├── user_modules/
  ├── onboarding_app/
  ├── streamlit_admin_app.py
  ├── streamlit_user_app.py
  ├── streamlit_onboarding_app.py
  ├── config/
  ├── customers/
  │   └── {customer_id}/
  │       ├── config/
  │       │   ├── branding.json
  │       │   ├── keywords.json
  │       │   └── feeds.json
  │       ├── customer_info.json
  │       ├── user_access.json
  │       └── data/
  │           ├── database.xlsx
  │           └── newsletters/
  ├── requirements.txt
  └── README.md
  ```
- Use caching where appropriate
- Batch operations when possible
- Error handling for network issues

### Streamlit Best Practices:
- Use session state for multi-step forms
- Cache expensive operations with `@st.cache_data`
- Use columns for layout
- Error handling with try/except and user-friendly messages

---

## Document Revision History

- **2025-01-XX:** Initial implementation plan created

