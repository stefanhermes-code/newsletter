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
    
    st.sidebar.markdown("---")
    
    # Main navigation
    available_pages = ["Dashboard", "Newsletters"]
    
    # Check if user has config edit permission
    has_edit_config = customer_selector.has_permission(user_email, current_customer_id, "edit_config")
    if has_edit_config:
        available_pages.append("Configuration")
    
    # All authenticated users can change their password via Settings
    available_pages.append("Settings")
    
    page = st.sidebar.selectbox("Navigation", available_pages)
    
    # Load customer config
    customer_config = customer_selector.load_customer_config(current_customer_id)
    
    # Update page title based on branding
    if customer_config.get('branding', {}).get('application_name'):
        branding_name = customer_config['branding']['application_name']
        st.set_page_config(page_title=branding_name, layout="wide")
    
    # Main content area
    if page == "Dashboard":
        render_dashboard(customer_config, current_newsletter, user_email, current_customer_id)
    elif page == "Newsletters":
        render_newsletters_viewer(current_customer_id, current_newsletter, user_email)
    elif page == "Configuration":
        if has_edit_config:
            render_configuration(current_customer_id, user_email)
        else:
            st.error("You don't have permission to edit configuration. Premium tier required.")
            st.info("Use the 'Settings' tab to change your password.")
    elif page == "Settings":
        render_settings(current_customer_id, user_email)

def render_dashboard(customer_config, current_newsletter, user_email, customer_id):
    """Main dashboard - news finding and newsletter generation"""
    branding = customer_config.get('branding', {})
    app_name = branding.get('application_name', 'Newsletter')
    
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
                            
                            # Clear selection after generation
                            st.session_state.selected_article_ids = set()
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
    tab1, tab2, tab3 = st.tabs(["Keywords", "RSS Feeds", "Change Password"])
    
    with tab1:
        config_manager.render_keywords_editor(customer_id, user_email)
    
    with tab2:
        config_manager.render_feeds_editor(customer_id, user_email)
    
    with tab3:
        password_manager.render_password_change(customer_id, user_email)

def render_settings(customer_id, user_email):
    """Settings page (for all users - password change)"""
    st.title("Settings")
    password_manager.render_password_change(customer_id, user_email)

if __name__ == "__main__":
    main()

