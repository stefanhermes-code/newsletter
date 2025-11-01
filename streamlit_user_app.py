"""
User Application (Multi-Tenant)

Newsletter generation application where users can switch between multiple newsletters.
"""

import streamlit as st

# Page configuration (will be updated when customer is selected)
st.set_page_config(
    page_title="Newsletter Tool",
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

def get_user_email():
    """Get user email - placeholder for now"""
    # TODO: Implement email input or authentication
    if st.session_state.user_email is None:
        return None
    return st.session_state.user_email

def get_user_newsletters(user_email):
    """Get user's accessible newsletters - placeholder"""
    # TODO: Implement GitHub API call to scan user_access.json files
    return []

def main():
    # Get user email (placeholder - will be implemented)
    user_email = get_user_email()
    
    # If no email, show login/email input
    if user_email is None:
        st.title("Newsletter Tool")
        st.header("Welcome!")
        
        with st.form("user_email_form"):
            email = st.text_input("Enter your email address", type="default")
            submitted = st.form_submit_button("Continue", type="primary")
            
            if submitted and email:
                st.session_state.user_email = email
                st.rerun()
        
        st.info("Enter your email to access your newsletters")
        return
    
    # Get user's accessible newsletters
    user_newsletters = get_user_newsletters(user_email)
    
    if not user_newsletters:
        st.title("No Newsletters Available")
        st.warning("You don't have access to any newsletters yet. Please contact your administrator.")
        return
    
    # Newsletter selector (always visible in sidebar)
    st.sidebar.title("📰 Newsletter")
    
    newsletter_options = {n['name']: n['customer_id'] for n in user_newsletters}
    newsletter_names = list(newsletter_options.keys())
    
    # Determine current newsletter index
    if st.session_state.current_customer_id:
        current_index = next((i for i, n in enumerate(user_newsletters) 
                            if n['customer_id'] == st.session_state.current_customer_id), 0)
    else:
        current_index = 0
        st.session_state.current_customer_id = user_newsletters[0]['customer_id']
    
    # Newsletter selector dropdown
    selected_name = st.sidebar.selectbox(
        "Switch Newsletter",
        newsletter_names,
        index=current_index,
        key="newsletter_selector"
    )
    
    # Update current customer if selection changed
    new_customer_id = newsletter_options[selected_name]
    if new_customer_id != st.session_state.current_customer_id:
        st.session_state.current_customer_id = new_customer_id
        st.rerun()
    
    # Get current newsletter info
    current_newsletter = next((n for n in user_newsletters 
                              if n['customer_id'] == st.session_state.current_customer_id), None)
    
    if current_newsletter:
        # Show tier indicator
        st.sidebar.info(f"**Tier:** {current_newsletter.get('tier', 'Unknown').title()}")
    
    st.sidebar.markdown("---")
    
    # Main navigation
    available_pages = ["Dashboard", "Newsletters"]
    
    # Check if user has config edit permission (placeholder)
    has_edit_config = current_newsletter and current_newsletter.get('permissions', []).count('edit_config') > 0
    if has_edit_config:
        available_pages.append("Configuration")
    
    page = st.sidebar.selectbox("Navigation", available_pages)
    
    # Load customer config (placeholder)
    customer_config = {}  # TODO: Load from GitHub
    
    # Main content area
    if page == "Dashboard":
        render_dashboard(customer_config, current_newsletter)
    elif page == "Newsletters":
        render_newsletters_viewer(st.session_state.current_customer_id, current_newsletter)
    elif page == "Configuration":
        if has_edit_config:
            render_configuration(st.session_state.current_customer_id, current_newsletter)
        else:
            st.error("You don't have permission to edit configuration. Premium tier required.")

def render_dashboard(customer_config, user_permissions):
    """Main dashboard - news finding and newsletter generation"""
    st.title(f"Dashboard - {customer_config.get('branding', {}).get('application_name', 'Newsletter')}")
    
    st.info("Dashboard functionality - Coming soon")
    
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
        find_button = st.button("🔍 Find News", type="primary", disabled=True)
    
    if find_button:
        st.success("Finding news... (Functionality coming soon)")
    
    st.markdown("---")
    
    # Article Dashboard
    st.header("Articles")
    st.info("Article dashboard will appear here")
    
    st.markdown("---")
    
    # Newsletter Generation
    st.header("Generate Newsletter")
    
    # Check if user has generate permission
    can_generate = user_permissions and 'generate' in user_permissions.get('permissions', [])
    
    if can_generate:
        selected_count = st.number_input("Selected Articles", value=0, disabled=True)
        generate_button = st.button("📰 Generate Newsletter", type="primary", disabled=True)
        if generate_button:
            st.success("Generating newsletter... (Functionality coming soon)")
    else:
        st.warning("You don't have permission to generate newsletters. Standard or Premium tier required.")

def render_newsletters_viewer(customer_id, user_permissions):
    """View generated newsletters"""
    st.title("Generated Newsletters")
    st.info("Newsletter viewer - Coming soon")
    
    st.write(f"Newsletters for customer: {customer_id}")
    st.write("Newsletter list will appear here")

def render_configuration(customer_id, user_permissions):
    """Configuration management (only if user has edit_config permission)"""
    st.title("Configuration")
    st.info("Configuration editor - Coming soon")
    
    tab1, tab2 = st.tabs(["Keywords", "RSS Feeds"])
    
    with tab1:
        st.write("Keywords configuration will appear here")
        st.write("(Editable - user has edit_config permission)")
    
    with tab2:
        st.write("RSS feeds configuration will appear here")
        st.write("(Editable - user has edit_config permission)")

if __name__ == "__main__":
    main()

