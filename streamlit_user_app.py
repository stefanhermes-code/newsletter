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
    
    # Logout button in sidebar (FIRST)
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
    
    st.sidebar.markdown("---")
    
    # Main navigation (SECOND)
    available_pages = ["Dashboard", "Newsletters"]
    
    # Initialize current customer ID from session state (needed for permission check)
    if 'current_customer_id' not in st.session_state:
        if user_newsletters:
            st.session_state.current_customer_id = user_newsletters[0]['customer_id']
        else:
            st.session_state.current_customer_id = None
    
    current_customer_id = st.session_state.current_customer_id
    
    # Check if user has config edit permission
    has_edit_config = customer_selector.has_permission(user_email, current_customer_id, "edit_config")
    if has_edit_config:
        available_pages.append("Configuration")
    
    # Preserve page selection in session state to prevent unwanted navigation changes
    if 'user_app_current_page' not in st.session_state:
        st.session_state.user_app_current_page = "Dashboard"
    
    # Get current page from session state (this is the source of truth)
    current_page_from_state = st.session_state.user_app_current_page
    
    # Find index for selectbox
    current_page_idx = 0
    if current_page_from_state in available_pages:
        current_page_idx = available_pages.index(current_page_from_state)
    
    # Navigation title for consistent styling with Company
    st.sidebar.title("🧭 Navigation")
    
    # Render navigation selectbox (label hidden for consistent font sizing)
    page = st.sidebar.selectbox(
        "Select page",
        available_pages,
        index=current_page_idx,  # Use index from session state
        key="user_app_nav_selectbox",
        label_visibility="collapsed"
    )
    
    # Update session state when page changes
    if page != st.session_state.user_app_current_page:
        st.session_state.user_app_current_page = page
    
    st.sidebar.markdown("---")
    
    # Company Selector (THIRD - renamed from "Newsletter")
    st.sidebar.title("🏢 Company")
    
    # Newsletter selector dropdown - SIMPLE DIRECT IMPLEMENTATION
    if user_newsletters and len(user_newsletters) > 0:
        newsletter_names = [n['name'] for n in user_newsletters]
        
        # Find current index
        current_index = 0
        if current_customer_id:
            current_index = next(
                (i for i, n in enumerate(user_newsletters) 
                 if n['customer_id'] == current_customer_id),
                0
            )
        
        selected_name = st.sidebar.selectbox(
            "Select company",
            newsletter_names,
            index=current_index,
            key="company_selector_sidebar",
            label_visibility="collapsed"
        )
        
        # Get selected customer ID
        selected_customer_id = next(
            n['customer_id'] for n in user_newsletters 
            if n['name'] == selected_name
        )
        
        # Update if changed (only rerun if actually changed)
        if selected_customer_id != current_customer_id:
            # Remember previous company to clear any per-company caches
            previous_customer_id = current_customer_id
            
            # Update current company in session state (single source of truth)
            st.session_state.current_customer_id = selected_customer_id
            current_customer_id = selected_customer_id
            
            # Clear any cached customer configs to force fresh load after rerun
            # Clear for previous company
            prev_key = f'customer_config_{previous_customer_id}'
            if previous_customer_id and prev_key in st.session_state:
                del st.session_state[prev_key]
            # Clear for new company (in case it existed)
            new_key = f'customer_config_{current_customer_id}'
            if new_key in st.session_state:
                del st.session_state[new_key]
            # Clear any residual keys matching the pattern just to be safe
            keys_to_delete = [k for k in st.session_state.keys() if str(k).startswith('customer_config_')]
            for k in keys_to_delete:
                if k not in ('user_app_current_page', 'current_customer_id'):
                    try:
                        del st.session_state[k]
                    except Exception:
                        pass
            # Preserve page selection
            if 'user_app_current_page' not in st.session_state:
                st.session_state.user_app_current_page = "Dashboard"
            st.rerun()
    
    # Ensure we have a valid customer ID
    if not current_customer_id and user_newsletters:
        current_customer_id = user_newsletters[0]['customer_id']
        st.session_state.current_customer_id = current_customer_id
    
    # Get current newsletter info (no tier display needed)
    current_newsletter = next((n for n in user_newsletters 
                              if n['customer_id'] == current_customer_id), None)
    
    # Note: Customer logo only shown in dashboard header, NOT in sidebar
    # Sidebar always shows GNP logo only
    
    # Load customer config
    customer_config = customer_selector.load_customer_config(current_customer_id)
    
    # Update page title based on branding
    if customer_config.get('branding', {}).get('application_name'):
        branding_name = customer_config['branding']['application_name']
        st.set_page_config(page_title=branding_name, layout="wide")
    
    # Main content area
    # Ensure current_customer_id is from session state (single source of truth)
    current_customer_id = st.session_state.get('current_customer_id')
    if not current_customer_id and user_newsletters:
        current_customer_id = user_newsletters[0]['customer_id']
        st.session_state.current_customer_id = current_customer_id
    
    # Reload config and newsletter info for current customer
    customer_config = customer_selector.load_customer_config(current_customer_id)
    current_newsletter = next((n for n in user_newsletters 
                              if n['customer_id'] == current_customer_id), None)
    
    if page == "Dashboard":
        render_dashboard(customer_config, current_newsletter, user_email, current_customer_id, user_newsletters)
    elif page == "Newsletters":
        render_newsletters_viewer(current_customer_id, current_newsletter, user_email)
    elif page == "Configuration":
        # Re-check permission for current customer (in case company changed)
        has_edit_config_current = customer_selector.has_permission(user_email, current_customer_id, "edit_config")
        if has_edit_config_current:
            render_configuration(current_customer_id, user_email)
        else:
            st.error("You don't have permission to edit configuration. Premium tier required.")

def render_dashboard(customer_config, current_newsletter, user_email, customer_id, user_newsletters):
    """Main dashboard - news finding and newsletter generation"""
    branding = customer_config.get('branding', {})
    app_name = branding.get('application_name', 'Newsletter')
    
    # Display customer logo and title (NO newsletter switcher - removed per user request)
    logo_path = branding.get('logo_path', '')
    
    # Simple layout: logo and title
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

    # Optional diagnostics
    with st.expander("Diagnostics (optional)"):
        st.caption("Use to troubleshoot when results are empty.")
        current_company_debug = st.session_state.get('current_customer_id', customer_id)
        st.write(f"Current company: `{current_company_debug}`")
        try:
            debug_keywords = [k for k in config_manager.load_keywords(customer_id) if k]
        except Exception:
            debug_keywords = []
        try:
            debug_feeds_cfg = config_manager.load_feeds(customer_id)
            debug_feed_urls = [f.get('url', '') for f in debug_feeds_cfg if f.get('enabled', True)]
        except Exception:
            debug_feed_urls = []
        st.write(f"Keywords: {len(debug_keywords)} (showing up to 5): {debug_keywords[:5]}")
        st.write(f"Feeds: {len(debug_feed_urls)} (showing up to 5): {debug_feed_urls[:5]}")
        debug_mode = st.checkbox("Enable detailed debug for this run", key="enable_debug_news_run", value=False)
    
    # Find news functionality
    if find_button or st.session_state.is_finding_news:
        if not st.session_state.is_finding_news:
            st.session_state.is_finding_news = True
        
        with st.spinner("Finding news articles..."):
            try:
                # Get current customer ID from session state (ensure it's up to date)
                current_customer_id = st.session_state.get('current_customer_id', customer_id)
                if not current_customer_id:
                    st.error("No company selected. Please select a company from the sidebar.")
                    st.session_state.is_finding_news = False
                    st.stop()
                
                # Get keywords and feeds
                keywords = [k for k in config_manager.load_keywords(current_customer_id) if k]
                feeds_config = config_manager.load_feeds(current_customer_id)
                feed_urls = [f['url'] for f in feeds_config if f.get('enabled', True)]
                
                # Check if we have keywords or feeds
                if not keywords and not feed_urls:
                    st.warning("No keywords or RSS feeds configured. Please configure them in the Configuration section.")
                    st.session_state.is_finding_news = False
                    st.stop()
                
                # Progress + streaming placeholders
                status_placeholder = st.empty()
                count_placeholder = st.empty()
                stream_placeholder = st.empty()
                
                def progress_callback(message):
                    status_placeholder.info(message)
                
                # Initialize accumulators and reset previous results for this run
                st.session_state.found_articles = []
                seen_urls_stream = set()
                
                # STREAM GOOGLE RESULTS INCREMENTALLY
                if keywords:
                    progress_callback("🔍 Searching Google News…")
                    for kw in keywords:
                        try:
                            google_batch = news_finder.find_news_google([kw], time_period)
                            for a in google_batch:
                                url = a.get('url')
                                if url and url not in seen_urls_stream:
                                    st.session_state.found_articles.append(a)
                                    seen_urls_stream.add(url)
                            # Update running count and a small rolling preview (last 10 titles)
                            count_placeholder.info(f"Google results so far: {len([a for a in st.session_state.found_articles if a.get('found_via')=='google'])} | Total: {len(st.session_state.found_articles)}")
                            latest = st.session_state.found_articles[-10:]
                            stream_titles = "\n".join([f"- {a.get('title','')[:100]}" for a in latest if a.get('title')])
                            stream_placeholder.markdown(f"**Latest articles:**\n\n{stream_titles}")
                        except Exception as e:
                            st.warning(f"Google error for keyword '{kw}': {e}")
                
                # STREAM RSS RESULTS INCREMENTALLY
                if feed_urls:
                    progress_callback("📡 Checking RSS feeds…")
                    for feed_url in feed_urls:
                        try:
                            rss_batch = news_finder.find_news_rss([feed_url], time_period)
                            for a in rss_batch:
                                url = a.get('url')
                                if url and url not in seen_urls_stream:
                                    st.session_state.found_articles.append(a)
                                    seen_urls_stream.add(url)
                            count_placeholder.info(f"Including RSS: {len(st.session_state.found_articles)} total")
                            latest = st.session_state.found_articles[-10:]
                            stream_titles = "\n".join([f"- {a.get('title','')[:100]}" for a in latest if a.get('title')])
                            stream_placeholder.markdown(f"**Latest articles:**\n\n{stream_titles}")
                        except Exception as e:
                            st.warning(f"RSS error for feed '{feed_url}': {e}")
                
                # Finalize
                articles = sorted(st.session_state.found_articles, key=lambda x: x.get('published_datetime', ''), reverse=True)
                
                st.session_state.found_articles = articles
                st.session_state.is_finding_news = False
                status_placeholder.empty()
                
                if articles:
                    st.success(f"✅ Found {len(articles)} articles")
                else:
                    st.info("No articles found. Try adjusting your keywords or time period.")
                    
            except Exception as e:
                st.error(f"Error finding news: {str(e)}")
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
    # Header with customer logo and title (consistent with Dashboard)
    customer_config = customer_selector.load_customer_config(customer_id)
    branding = customer_config.get('branding', {})
    app_name = branding.get('application_name', 'Newsletter')
    logo_path = branding.get('logo_path', '')

    if logo_path:
        try:
            col_logo, col_title = st.columns([1, 4])
            with col_logo:
                st.image(logo_path, width=150)
            with col_title:
                st.title(f"📰 Generated Newsletters - {app_name}")
        except:
            st.title(f"📰 Generated Newsletters - {app_name}")
    else:
        st.title(f"📰 Generated Newsletters - {app_name}")
    
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
    # Header with customer logo and title (consistent with Dashboard)
    customer_config = customer_selector.load_customer_config(customer_id)
    branding = customer_config.get('branding', {})
    app_name = branding.get('application_name', 'Newsletter')
    logo_path = branding.get('logo_path', '')

    if logo_path:
        try:
            col_logo, col_title = st.columns([1, 4])
            with col_logo:
                st.image(logo_path, width=150)
            with col_title:
                st.title(f"⚙️ Configuration - {app_name}")
        except:
            st.title(f"⚙️ Configuration - {app_name}")
    else:
        st.title(f"⚙️ Configuration - {app_name}")
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

