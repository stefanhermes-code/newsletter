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
            
            # (legal disclaimer removed per requirements)
            
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
        previous_page = st.session_state.user_app_current_page
        
        # Clear Dashboard-specific state when navigating away from Dashboard
        if previous_page == "Dashboard":
            st.session_state.pop('last_newsletter_html', None)
            st.session_state.pop('last_newsletter_filename', None)
            st.session_state.found_articles = []
            st.session_state.selected_article_ids = set()
            st.session_state.is_finding_news = False
        
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
            # Clear search/results, selections and last preview when switching company
            st.session_state.found_articles = []
            st.session_state.selected_article_ids = set()
            st.session_state.pop('last_newsletter_html', None)
            st.session_state.pop('last_newsletter_filename', None)
            
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

    from user_modules.category_mapper import (
        available_search_categories,
        load_category_config,
        merge_search_keywords,
        keywords_for_categories,
    )

    all_keywords = [k for k in config_manager.load_keywords(customer_id) if k]
    category_config = load_category_config(customer_id)
    search_categories = available_search_categories(category_config, all_keywords)

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

    if search_categories:
        selected_categories = st.multiselect(
            "Search by category",
            options=search_categories,
            default=[],
            key="search_categories",
            help="Select one or more categories to search all keywords mapped to them.",
        )
    else:
        selected_categories = []
        st.caption("No category mappings configured — use individual keywords below.")

    category_keyword_set = set(
        keywords_for_categories(selected_categories, all_keywords, category_config)
    )
    # Individual picks: all keywords, with those already covered by categories shown as selected info
    keyword_options = all_keywords
    selected_keywords = st.multiselect(
        "Search by individual keyword",
        options=keyword_options,
        default=[],
        key="search_keywords",
        help="Add specific keywords on top of (or instead of) categories.",
    )

    search_keywords = merge_search_keywords(
        selected_categories, selected_keywords, all_keywords, category_config
    )
    if selected_categories or selected_keywords:
        covered_by_cat = len(category_keyword_set)
        extra = len([k for k in selected_keywords if k not in category_keyword_set])
        st.caption(
            f"Will search **{len(search_keywords)}** keyword(s)"
            + (f" ({covered_by_cat} from categories" + (f", {extra} extra" if extra else "") + ")" if selected_categories else "")
            + "."
        )
    else:
        st.info("Select at least one category and/or keyword to search.")

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

                if not search_keywords:
                    st.warning("Select at least one category or keyword before searching.")
                    st.session_state.is_finding_news = False
                    st.stop()

                feeds_config = config_manager.load_feeds(current_customer_id)
                feed_urls = [f['url'] for f in feeds_config if f.get('enabled', True)]
                # Temporarily disable RSS fetching (bogus URLs causing long loops)
                feed_urls = []

                keywords = search_keywords
                
                # Find news in one pass (streaming and diagnostics removed)
                articles = news_finder.find_news_background(
                    keywords=keywords,
                    feed_urls=feed_urls,
                    time_period=time_period,
                    progress_callback=None
                )
                
                st.session_state.found_articles = articles
            except Exception as e:
                st.error(f"Error finding news: {str(e)}")
            finally:
                # Always finalize to avoid stuck spinner
                st.session_state.is_finding_news = False
                
                
                if articles:
                    st.success(f"✅ Found {len(articles)} articles")
                else:
                    st.info("No articles found. Try adjusting your keywords or time period.")
    
    st.markdown("---")
    
    # Newsletter Generation (moved up for better UX)
    st.header("📰 Generate Newsletter")
    can_generate = current_newsletter and 'generate' in current_newsletter.get('permissions', [])
    if can_generate:
        # Show last preview if available
        if st.session_state.get('last_newsletter_html'):
            st.markdown("### Newsletter Preview")
            st.components.v1.html(st.session_state['last_newsletter_html'], height=600, scrolling=True)
            if st.session_state.get('last_newsletter_filename'):
                newsletter_generator.download_newsletter(st.session_state['last_newsletter_html'], st.session_state['last_newsletter_filename'])
            newsletter_generator.download_linkedin_banner()

        selected_count = len(st.session_state.selected_article_ids)
        st.write(f"**{selected_count} articles selected**")
        if selected_count == 0:
            st.warning("Please select at least one article to generate a newsletter.")
        else:
            from user_modules.category_mapper import draft_intro_from_articles, load_category_config, assign_sections
            from user_modules import shortio_client

            short_name = customer_config.get('branding', {}).get('short_name') or customer_id.upper()
            category_config = load_category_config(customer_id)
            selected_articles_preview = article_dashboard.select_articles(
                list(st.session_state.selected_article_ids),
                st.session_state.found_articles
            )
            drafted = draft_intro_from_articles(
                assign_sections(selected_articles_preview, category_config),
                category_config
            ) if selected_articles_preview else ""

            # Keep user edits across reruns unless selection signature changes
            selection_key = ",".join(sorted(st.session_state.selected_article_ids))
            if st.session_state.get("_intro_selection_key") != selection_key:
                st.session_state["_intro_selection_key"] = selection_key
                st.session_state["newsletter_intro_input"] = drafted
            if "newsletter_announcements_input" not in st.session_state:
                st.session_state["newsletter_announcements_input"] = ""

            st.markdown("#### Introduction & announcements")
            intro_text = st.text_area(
                "A. What's in this newsletter (3–4 sentences — editable)",
                height=120,
                key="newsletter_intro_input",
            )
            announcements = st.text_area(
                "B. APBA announcements & upcoming events (manual)",
                height=100,
                key="newsletter_announcements_input",
                placeholder="Events, member notices, deadlines…",
            )

            use_shortio = True
            if shortio_client.is_configured():
                use_shortio = st.checkbox(
                    "Create Short.io tracked links (old links cleaned after ~60 days)",
                    value=True,
                    key="use_shortio_links",
                )
            else:
                st.caption("Short.io not configured — article URLs will be used as-is.")

            generate_button = st.button("📰 Generate Newsletter", type="primary")
            if generate_button:
                selected_articles = selected_articles_preview
                if selected_articles:
                    with st.spinner("Generating newsletter..."):
                        filename = newsletter_generator.generate_newsletter(
                            selected_articles=selected_articles,
                            branding=branding,
                            customer_id=customer_id,
                            short_name=short_name,
                            intro_text=intro_text,
                            announcements=announcements,
                            use_shortio=use_shortio,
                        )
                        if filename:
                            st.success(f"Newsletter generated and saved: {filename}")
                            st.markdown("### Newsletter Preview")
                            st.components.v1.html(st.session_state.last_newsletter_html, height=600, scrolling=True)
                            newsletter_generator.download_newsletter(
                                st.session_state.last_newsletter_html, filename
                            )
                            newsletter_generator.download_linkedin_banner()
                            st.session_state.selected_article_ids = set()
                else:
                    st.error("Failed to retrieve selected articles.")
    else:
        st.warning("You don't have permission to generate newsletters. Standard or Premium tier required.")
    
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
    
    # (newsletter generation moved above)

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

    can_generate = current_newsletter and 'generate' in current_newsletter.get('permissions', [])

    # --- Upgrade old HTML to new format ---
    st.header("🔄 Upgrade old newsletter HTML")
    st.caption(
        "Convert a legacy flat HTML newsletter into the new format "
        "(categories, intro, announcements, banner, inline dates)."
    )
    upgrade_source = st.radio(
        "Source",
        ["Upload HTML file", "Pick saved newsletter"],
        horizontal=True,
        key="upgrade_source",
    )

    uploaded_html = None
    selected_saved = None
    newsletters = list_newsletters(customer_id)

    if upgrade_source == "Upload HTML file":
        uploaded = st.file_uploader(
            "Upload newsletter .html",
            type=["html", "htm"],
            key="upgrade_upload",
        )
        if uploaded:
            uploaded_html = uploaded.read().decode("utf-8", errors="replace")
            selected_saved = uploaded.name
    else:
        names = [n["name"] for n in newsletters] if newsletters else []
        if names:
            selected_saved = st.selectbox("Saved newsletter", names, key="upgrade_pick")
            if selected_saved:
                uploaded_html = get_newsletter_content(customer_id, selected_saved)
        else:
            st.info("No saved newsletters found. Upload a file instead.")

    if uploaded_html:
        from user_modules.newsletter_upgrade import (
            is_new_format,
            parse_newsletter_html,
            upgrade_html_content,
        )
        from user_modules.newsletter_generator import download_newsletter, download_linkedin_banner

        arts_preview, meta_preview = parse_newsletter_html(uploaded_html)
        st.write(
            f"Detected **{len(arts_preview)}** article(s)"
            + (f" — title: {meta_preview.get('title')}" if meta_preview.get("title") else "")
            + (" · already new-format (can still re-apply)" if is_new_format(uploaded_html) else " · legacy format")
        )

        if can_generate:
            upgrade_intro = st.text_area(
                "A. Introduction (optional — auto-drafted if empty)",
                height=100,
                key="upgrade_intro",
            )
            upgrade_announcements = st.text_area(
                "B. APBA announcements & upcoming events (optional)",
                height=80,
                key="upgrade_announcements",
                placeholder="Events, member notices…",
            )
            from user_modules import shortio_client

            upgrade_shortio = False
            if shortio_client.is_configured():
                upgrade_shortio = st.checkbox(
                    "Also create Short.io tracked links",
                    value=False,
                    key="upgrade_shortio",
                )
            overwrite = st.checkbox(
                "Overwrite original file when saving",
                value=False,
                key="upgrade_overwrite",
                help="If unchecked, saves as …_upgraded.html",
            )

            if st.button("✨ Upgrade to new HTML", type="primary", key="upgrade_run"):
                with st.spinner("Upgrading newsletter..."):
                    keywords = [k for k in config_manager.load_keywords(customer_id) if k]
                    new_html, articles, meta = upgrade_html_content(
                        uploaded_html,
                        customer_id=customer_id,
                        branding=branding,
                        all_keywords=keywords,
                        intro_text=upgrade_intro,
                        announcements=upgrade_announcements,
                        use_shortio=upgrade_shortio,
                    )
                    if not new_html:
                        st.error("Could not find articles in this HTML.")
                    else:
                        base_name = selected_saved or "Newsletter_upgraded.html"
                        if not base_name.lower().endswith(".html"):
                            base_name += ".html"
                        if overwrite:
                            out_name = base_name
                        else:
                            out_name = base_name.replace(".html", "_upgraded.html")
                            if out_name == base_name:
                                out_name = f"{base_name}_upgraded.html"

                        from user_modules.github_user import save_newsletter

                        if save_newsletter(
                            customer_id,
                            new_html,
                            out_name,
                            commit_message=f"Upgrade newsletter to new format: {out_name}",
                        ):
                            st.success(f"Upgraded and saved: {out_name} ({len(articles)} articles)")
                            st.session_state["last_newsletter_html"] = new_html
                            st.session_state["last_newsletter_filename"] = out_name
                            st.components.v1.html(new_html, height=600, scrolling=True)
                            download_newsletter(new_html, out_name)
                            download_linkedin_banner()
                        else:
                            st.error("Upgrade built HTML but failed to save to GitHub.")
                            st.session_state["last_newsletter_html"] = new_html
                            download_newsletter(new_html, out_name)
        else:
            st.warning("You need generate permission to upgrade and save newsletters.")

    st.markdown("---")
    
    # Load newsletters from GitHub
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

