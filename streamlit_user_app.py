"""
User Application (Multi-Tenant) - GlobalNewsPilot

Newsletter generation application where users can switch between multiple newsletters.
"""

import streamlit as st
from user_modules import customer_selector
from user_modules import news_finder
from user_modules import article_dashboard
from user_modules import newsletter_generator
from user_modules import config_manager
from user_modules import password_manager
from user_modules.github_user import list_newsletters, get_newsletter_content
from datetime import datetime

# Page configuration (will be updated when customer is selected)
st.set_page_config(
    page_title="GlobalNewsPilot",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'user_email' not in st.session_state:
    st.session_state.user_email = None

if 'current_customer_id' not in st.session_state:
    st.session_state.current_customer_id = None

if 'user_newsletters' not in st.session_state:
    st.session_state.user_newsletters = []

if 'selected_article_ids' not in st.session_state:
    st.session_state.selected_article_ids = set()

if 'found_articles' not in st.session_state:
    st.session_state.found_articles = []

if 'is_finding_news' not in st.session_state:
    st.session_state.is_finding_news = False

def main():
    # Check authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Get user email if authenticated
    user_email = customer_selector.get_user_email() if st.session_state.authenticated else None
    
    # If not authenticated, show login form
    if not st.session_state.authenticated:
        # Display GNP logo at top
        import os
        from pathlib import Path
        
        # Try multiple possible locations (assets folder for GitHub, root for local)
        logo_paths = [
            "assets/GNP Logo.png",  # GitHub location (primary)
            "assets/GNP logo.png",
            "GNP Logo.png",  # Root directory (local fallback)
            "GNP logo.png"
        ]
        
        logo_displayed = False
        for logo_path in logo_paths:
            # Check if file exists locally
            if os.path.exists(logo_path):
                try:
                    st.image(logo_path, width=200)  # Fixed width instead of full container
                    logo_displayed = True
                    break
                except Exception as e:
                    continue
        
        # If not found locally, try to display (for Streamlit Cloud/GitHub)
        if not logo_displayed:
            for logo_path in logo_paths:
                try:
                    st.image(logo_path, width=200)  # Fixed width instead of full container
                    logo_displayed = True
                    break
                except:
                    continue
        
        st.title("📰 GlobalNewsPilot")
        st.header("Welcome!")
        st.markdown("Please enter your credentials to access your newsletters.")
        
        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="user@company.com", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            # Legal disclaimer (same as PI3)
            st.caption("By submitting content (including files), you confirm you have the right to share it and grant PU ExpertCenter/PI3 a worldwide, royalty‑free license to use it to operate, secure, and improve the service. You waive any claims arising from such permitted use, to the maximum extent allowed by law. Do not upload confidential or personal data. This service is informational only and not engineering, legal, or safety advice.")
            
            submitted = st.form_submit_button("Login", type="primary")
            
            if submitted:
                if email and password:
                    # Authenticate user
                    is_authenticated, error_message, user_data = customer_selector.authenticate_user(email, password)
                    
                    if is_authenticated:
                        # Check if user is already logged in elsewhere
                        if customer_selector.is_user_logged_in_elsewhere(email):
                            st.error("This email address is already logged in elsewhere. Only one session per email is allowed.")
                        else:
                            # Login successful
                            st.session_state.authenticated = True
                            customer_selector.set_user_email(email)
                            st.session_state.current_user = email
                            if user_data:
                                st.session_state.valid_until = user_data.get("valid_until", "")
                            st.success("Login successful!")
                            st.rerun()
                    else:
                        st.error(error_message)
                else:
                    st.error("Please enter both email and password.")
        
        return
    
    # Get user's accessible newsletters
    user_newsletters = customer_selector.get_user_newsletters(user_email)
    
    if not user_newsletters:
        st.title("No Newsletters Available")
        st.warning("You don't have access to any newsletters yet. Please contact your administrator.")
        return
    
    # Store newsletters in session state
    st.session_state.user_newsletters = user_newsletters
    
    # Display GNP logo in sidebar
    import os
    sidebar_logo_paths = [
        "assets/GNP Logo.png",  # GitHub location (primary)
        "assets/GNP logo.png",
        "GNP Logo.png",  # Root directory (local fallback)
        "GNP logo.png"
    ]
    sidebar_logo_found = False
    for path in sidebar_logo_paths:
        if os.path.exists(path):
            try:
                st.sidebar.image(path, width=150)  # Smaller width for sidebar
                st.sidebar.markdown("---")
                sidebar_logo_found = True
                break
            except Exception as e:
                continue
    if not sidebar_logo_found:
        # Try to display anyway (might work on Streamlit Cloud from GitHub)
        try:
            st.sidebar.image("assets/GNP Logo.png", width=150)  # Smaller width for sidebar
            st.sidebar.markdown("---")
        except:
            try:
                st.sidebar.image("GNP logo.png", width=150)  # Smaller width for sidebar
                st.sidebar.markdown("---")
            except:
                pass  # If logo not found, continue without it
    
    # Logout button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", key="logout_button"):
        st.session_state.authenticated = False
        st.session_state.user_email = None
        st.session_state.current_user = None
        st.session_state.current_customer_id = None
        st.session_state.user_newsletters = []
        st.session_state.selected_article_ids = set()
        st.session_state.found_articles = []
        st.rerun()
    
    # Newsletter selector (always visible in sidebar)
    st.sidebar.title("📰 Newsletter")
    
    # Use customer_selector module for newsletter selection
    current_customer_id = customer_selector.render_newsletter_selector(
        user_newsletters,
        customer_selector.get_current_customer()
    )
    
    if not current_customer_id:
        current_customer_id = user_newsletters[0]['customer_id'] if user_newsletters else None
    
    # Get current newsletter info
    current_newsletter = next((n for n in user_newsletters 
                              if n['customer_id'] == current_customer_id), None)
    
    if current_newsletter:
        # Show tier indicator
        st.sidebar.info(f"**Tier:** {current_newsletter.get('tier', 'Unknown').title()}")
    
    # Display customer logo in sidebar if available
    if current_customer_id:
        customer_config = customer_selector.load_customer_config(current_customer_id)
        branding = customer_config.get('branding', {})
        logo_path = branding.get('logo_path', '')
        if logo_path:
            try:
                st.sidebar.markdown("---")
                st.sidebar.image(logo_path, use_container_width=True)
            except:
                pass  # If logo not found, continue without it
    
    st.sidebar.markdown("---")
    
    # Main navigation
    available_pages = ["Dashboard", "Newsletters"]
    
    # Check if user has config edit permission
    has_edit_config = customer_selector.has_permission(user_email, current_customer_id, "edit_config")
    if has_edit_config:
        available_pages.append("Configuration")
    
    # Preserve page selection in session state to prevent unwanted navigation changes
    # Initialize if not exists, but NEVER override if it already exists (preserves user selection)
    if 'user_app_current_page' not in st.session_state:
        st.session_state.user_app_current_page = "Dashboard"
    
    # Get current page from session state (this is the source of truth)
    current_page_from_state = st.session_state.user_app_current_page
    
    # Find index for selectbox
    current_page_idx = 0
    if current_page_from_state in available_pages:
        current_page_idx = available_pages.index(current_page_from_state)
    
    # Render navigation selectbox
    # CRITICAL: Use session state as source of truth - force widget to match session state
    # The widget key ensures identity, but we control the value via index parameter
    nav_key = "user_app_nav_selectbox"
    
    # If widget exists in session state but doesn't match our desired page, update it
    # This handles cases where newsletter change causes rerun
    if nav_key in st.session_state:
        widget_value = st.session_state[nav_key]
        if widget_value != current_page_from_state:
            # Widget state doesn't match session state - force it to match
            # Delete the widget state so it resets to our index
            del st.session_state[nav_key]
    
    page = st.sidebar.selectbox(
        "Navigation", 
        available_pages, 
        index=current_page_idx,  # Force index from session state
        key=nav_key
    )
    
    # Only update session state if this is a genuine user change
    # (i.e., widget value differs from what we set it to)
    if page != current_page_from_state:
        # User manually changed navigation - update session state
        st.session_state.user_app_current_page = page
    
    # Load customer config
    customer_config = customer_selector.load_customer_config(current_customer_id)
    
    # Update page title based on branding
    if customer_config.get('branding', {}).get('application_name'):
        branding_name = customer_config['branding']['application_name']
        st.set_page_config(page_title=branding_name, layout="wide")
    
    # Main content area
    # IMPORTANT: Re-check current_customer_id from session state before rendering
    # This ensures dashboard dropdown changes are reflected immediately
    current_customer_id = customer_selector.get_current_customer() or current_customer_id
    if not current_customer_id and user_newsletters:
        current_customer_id = user_newsletters[0]['customer_id']
    
    # Reload config and newsletter info if customer changed
    if current_customer_id != customer_config.get('customer_id'):
        customer_config = customer_selector.load_customer_config(current_customer_id)
        current_newsletter = next((n for n in user_newsletters 
                                  if n['customer_id'] == current_customer_id), None)
    
    if page == "Dashboard":
        render_dashboard(customer_config, current_newsletter, user_email, current_customer_id, user_newsletters)
    elif page == "Newsletters":
        render_newsletters_viewer(current_customer_id, current_newsletter, user_email)
    elif page == "Configuration":
        if has_edit_config:
            render_configuration(current_customer_id, user_email)
        else:
            st.error("You don't have permission to edit configuration. Premium tier required.")

def render_dashboard(customer_config, current_newsletter, user_email, customer_id, user_newsletters):
    """Main dashboard - news finding and newsletter generation"""
    branding = customer_config.get('branding', {})
    app_name = branding.get('application_name', 'Newsletter')
    
    # Display customer logo and title with newsletter switcher
    logo_path = branding.get('logo_path', '')
    
    # If user has multiple newsletters, show switcher
    if len(user_newsletters) > 1:
        col_logo, col_title, col_switcher = st.columns([1, 3, 2])
        
        with col_logo:
            if logo_path:
                try:
                    st.image(logo_path, width=150)
                except:
                    pass
        
        with col_title:
            st.title(f"Dashboard - {app_name}")
        
        with col_switcher:
            st.write("")  # Spacing
            st.write("")  # Spacing
            
            # Newsletter switcher dropdown - syncs with sidebar via session state
            newsletter_options = {n['name']: n['customer_id'] for n in user_newsletters}
            newsletter_names = list(newsletter_options.keys())
            
            # Get current customer ID from session state (source of truth)
            current_customer_id_state = customer_selector.get_current_customer() or customer_id
            
            # Find current index
            current_index = next(
                (i for i, n in enumerate(user_newsletters) 
                 if n['customer_id'] == current_customer_id_state),
                0
            )
            
            # Dashboard selectbox - reads from and writes to same session state
            selected_name = st.selectbox(
                "📰 Switch Newsletter",
                newsletter_names,
                index=current_index,
                key="newsletter_selector_dashboard"
            )
            
            # Get selected customer ID
            selected_customer_id = newsletter_options[selected_name]
            
            # If changed, update session state (source of truth) and rerun
            # The rerun will cause sidebar to also update since it reads from same state
            if selected_customer_id != current_customer_id_state:
                # CRITICAL: Preserve the current page BEFORE rerun to prevent navigation change
                # Read current page from widget state if available, otherwise from session state
                current_page = st.session_state.get('user_app_current_page', 'Dashboard')
                # Explicitly preserve it
                st.session_state.user_app_current_page = current_page
                
                customer_selector.set_current_customer(selected_customer_id)
                # Clear any article selections when switching newsletters
                if 'selected_article_ids' in st.session_state:
                    st.session_state.selected_article_ids = set()
                if 'found_articles' in st.session_state:
                    st.session_state.found_articles = []
                st.rerun()
                return  # Exit early, rerun will show updated content
    else:
        # Single newsletter - just show logo and title
        if logo_path:
            try:
                col_logo, col_title = st.columns([1, 4])
                with col_logo:
                    st.image(logo_path, width=150)
                with col_title:
                    st.title(f"Dashboard - {app_name}")
            except:
                st.title(f"Dashboard - {app_name}")
        else:
            st.title(f"Dashboard - {app_name}")
    
    # News Finding Section
    st.header("📰 Find News")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        time_period = st.selectbox(
            "Time Period",
            ["Last 7 days", "Last 14 days", "Last 30 days"],
            key="time_period"
        )
    
    with col2:
        st.write("")
        st.write("")
        find_button = st.button("🔍 Find News", type="primary")
    
    # Find news functionality
    if find_button or st.session_state.is_finding_news:
        if not st.session_state.is_finding_news:
            st.session_state.is_finding_news = True
        
        with st.spinner("Finding news articles..."):
            # Get keywords and feeds
            keywords = [k for k in config_manager.load_keywords(customer_id) if k]
            feeds_config = config_manager.load_feeds(customer_id)
            feed_urls = [f['url'] for f in feeds_config if f.get('enabled', True)]
            
            # Progress callback
            status_placeholder = st.empty()
            
            def progress_callback(message):
                status_placeholder.info(message)
            
            # Find news
            articles = news_finder.find_news_background(
                keywords=keywords,
                feed_urls=feed_urls,
                time_period=time_period,
                progress_callback=progress_callback
            )
            
            st.session_state.found_articles = articles
            st.session_state.is_finding_news = False
            status_placeholder.empty()
    
    st.markdown("---")
    
    # Article Dashboard
    st.header("📋 Articles")
    
    # Show selected articles summary in sidebar
    if st.session_state.found_articles:
        selected_articles_list = article_dashboard.show_selected_summary(
            st.session_state.selected_article_ids,
            st.session_state.found_articles
        )
    
    # Display articles
    if st.session_state.found_articles:
        updated_selection = article_dashboard.display_articles(
            st.session_state.found_articles,
            st.session_state.selected_article_ids
        )
        st.session_state.selected_article_ids = updated_selection
    else:
        st.info("Click 'Find News' to search for articles based on your keywords and RSS feeds.")
    
    st.markdown("---")
    
    # Newsletter Generation
    st.header("📰 Generate Newsletter")
    
    # Check if user has generate permission
    can_generate = current_newsletter and 'generate' in current_newsletter.get('permissions', [])
    
    if can_generate:
        selected_count = len(st.session_state.selected_article_ids)
        st.write(f"**{selected_count} articles selected**")
        
        if selected_count == 0:
            st.warning("Please select at least one article to generate a newsletter.")
        else:
            # Get short name from branding or customer_id
            # Check if there's a 'short_name' in branding config (might be in a different structure)
            short_name = customer_config.get('branding', {}).get('short_name') or customer_id.upper()
            
            generate_button = st.button("📰 Generate Newsletter", type="primary")
            
            if generate_button:
                # Get selected articles
                selected_articles = article_dashboard.select_articles(
                    list(st.session_state.selected_article_ids),
                    st.session_state.found_articles
                )
                
                if selected_articles:
                    with st.spinner("Generating newsletter..."):
                        filename = newsletter_generator.generate_newsletter(
                            selected_articles=selected_articles,
                            branding=branding,
                            customer_id=customer_id,
                            short_name=short_name
                        )
                        
                        if filename:
                            st.success(f"Newsletter generated and saved: {filename}")
                            
                            # Get newsletter content for preview/download
                            newsletter_html = newsletter_generator.get_newsletter_preview(
                                selected_articles,
                                branding
                            )
                            
                            st.markdown("### Newsletter Preview")
                            st.components.v1.html(newsletter_html, height=600, scrolling=True)
                            
                            newsletter_generator.download_newsletter(newsletter_html, filename)
                            
                            # Clear selection after generation to prevent reusing articles
                            st.session_state.selected_article_ids = set()
                            st.rerun()
                else:
                    st.error("Failed to retrieve selected articles.")
    else:
        st.warning("You don't have permission to generate newsletters. Standard or Premium tier required.")

def render_newsletters_viewer(customer_id, current_newsletter, user_email):
    """View generated newsletters"""
    st.title("📰 Generated Newsletters")
    
    # Load newsletters from GitHub
    newsletters = list_newsletters(customer_id)
    
    if not newsletters:
        st.info("No newsletters generated yet. Go to Dashboard to create your first newsletter.")
        return
    
    st.write(f"**{len(newsletters)} newsletter(s) found**")
    st.markdown("---")
    
    # Display newsletters
    for newsletter in newsletters:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.markdown(f"### {newsletter['name']}")
                st.caption(f"Last modified: {newsletter.get('last_modified', 'Unknown')}")
                st.caption(f"Size: {newsletter.get('size', 0)} bytes")
            
            with col2:
                # View button
                if st.button("👁️ View", key=f"view_{newsletter['name']}"):
                    content = get_newsletter_content(customer_id, newsletter['name'])
                    if content:
                        st.markdown("### Newsletter Preview")
                        st.components.v1.html(content, height=600, scrolling=True)
            
            with col3:
                # Download button
                st.download_button(
                    label="📥 Download",
                    data=get_newsletter_content(customer_id, newsletter['name']) or "",
                    file_name=newsletter['name'],
                    mime="text/html",
                    key=f"download_{newsletter['name']}"
                )
            
            st.markdown("---")

def render_configuration(customer_id, user_email):
    """Configuration management (only if user has edit_config permission)"""
    tab1, tab2, tab3, tab4 = st.tabs(["Branding", "Keywords", "RSS Feeds", "Change Password"])
    
    with tab1:
        config_manager.render_branding_editor(customer_id, user_email)
    
    with tab2:
        config_manager.render_keywords_editor(customer_id, user_email)
    
    with tab3:
        config_manager.render_feeds_editor(customer_id, user_email)
    
    with tab4:
        password_manager.render_password_change(customer_id, user_email)

if __name__ == "__main__":
    main()

