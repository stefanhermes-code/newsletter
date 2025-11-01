"""
Admin Dashboard Application

Multi-customer management dashboard for Newsletter Tool Cloud.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Newsletter Tool - Admin Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'current_customer_id' not in st.session_state:
    st.session_state.current_customer_id = None

def main():
    # Sidebar navigation
    st.sidebar.title("📊 Admin Dashboard")
    st.sidebar.markdown("---")
    
    page = st.sidebar.selectbox(
        "Navigation",
        [
            "Overview",
            "Customer Management",
            "Customer Onboarding",
            "Configuration Viewer",
            "Activity Monitoring",
            "Analytics",
            "Export/Import"
        ]
    )
    
    # Initialize onboarding session state
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}
    
    # Main content area
    st.title("Newsletter Tool - Admin Dashboard")
    
    if page == "Overview":
        render_overview()
    elif page == "Customer Management":
        render_customer_management()
    elif page == "Customer Onboarding":
        render_customer_onboarding()
    elif page == "Configuration Viewer":
        render_config_viewer()
    elif page == "Activity Monitoring":
        render_activity_monitoring()
    elif page == "Analytics":
        render_analytics()
    elif page == "Export/Import":
        render_export_import()

def render_overview():
    """Overview/Dashboard page"""
    st.header("Overview")
    st.info("Admin dashboard overview - Coming soon")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", "0")
    with col2:
        st.metric("Active Customers", "0")
    with col3:
        st.metric("Total Newsletters", "0")
    with col4:
        st.metric("Pending Onboarding", "0")

def render_customer_management():
    """Customer Management page"""
    st.header("Customer Management")
    st.info("Customer CRUD operations - Coming soon")
    
    tab1, tab2, tab3 = st.tabs(["Customer List", "Customer Details", "User Access Management"])
    
    with tab1:
        st.write("Customer list will appear here")
        st.button("Add New Customer", type="primary")
    
    with tab2:
        st.write("Customer details view will appear here")
        st.info("Select a customer from the list to view details")
    
    with tab3:
        st.write("User access management will appear here")
        st.info("Manage user access and payment tiers for each customer")

def render_customer_onboarding():
    """Customer Onboarding page - Integrated into Admin App"""
    st.header("Customer Onboarding")
    
    tab1, tab2, tab3 = st.tabs(["New Customer Onboarding", "Pending Submissions", "Manual Entry"])
    
    with tab1:
        st.subheader("Onboard New Customer")
        st.write("Fill out the customer information below to create a new newsletter account.")
        
        # Step-by-step form (7 steps integrated here)
        if 'onboarding_step' not in st.session_state:
            st.session_state.onboarding_step = 1
        
        steps = ["Basic Info", "Branding", "Keywords", "Feeds", "Contact", "Review", "Create"]
        progress = st.session_state.onboarding_step / len(steps)
        st.progress(progress)
        st.caption(f"Step {st.session_state.onboarding_step} of {len(steps)}: {steps[st.session_state.onboarding_step - 1]}")
        
        with st.form(f"onboarding_form_step_{st.session_state.onboarding_step}"):
            if st.session_state.onboarding_step == 1:
                render_onboarding_step1_basic_info()
            elif st.session_state.onboarding_step == 2:
                render_onboarding_step2_branding()
            elif st.session_state.onboarding_step == 3:
                render_onboarding_step3_keywords()
            elif st.session_state.onboarding_step == 4:
                render_onboarding_step4_feeds()
            elif st.session_state.onboarding_step == 5:
                render_onboarding_step5_contact()
            elif st.session_state.onboarding_step == 6:
                render_onboarding_step6_review()
            elif st.session_state.onboarding_step == 7:
                render_onboarding_step7_create()
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.session_state.onboarding_step > 1:
                    if st.form_submit_button("← Back"):
                        st.session_state.onboarding_step -= 1
                        st.rerun()
            with col3:
                if st.session_state.onboarding_step < len(steps):
                    if st.form_submit_button("Next →", type="primary"):
                        st.session_state.onboarding_step += 1
                        st.rerun()
    
    with tab2:
        st.subheader("Pending Onboarding Submissions")
        st.info("Pending customer submissions will appear here (if using customer-facing form option)")
        st.write("Currently using direct admin entry - see 'New Customer Onboarding' tab")
    
    with tab3:
        st.subheader("Manual Entry (Quick Setup)")
        st.write("Quick manual entry for creating customers without full wizard")
        st.button("Create Customer (Quick)", disabled=True, help="Coming soon")

def render_onboarding_step1_basic_info():
    """Onboarding Step 1: Basic Information"""
    st.write("**Step 1: Basic Information**")
    
    customer_id = st.text_input("Customer ID *", 
                                help="Lowercase, alphanumeric only. Example: 'acme', 'htc', 'apba'",
                                value=st.session_state.get('onboarding_data', {}).get('customer_id', ''))
    company_name = st.text_input("Company Name *",
                                value=st.session_state.get('onboarding_data', {}).get('company_name', ''))
    short_name = st.text_input("Short Name *",
                              value=st.session_state.get('onboarding_data', {}).get('short_name', ''),
                              help="Used in file names. Example: 'ACME', 'HTC'")
    
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}
    st.session_state.onboarding_data['customer_id'] = customer_id
    st.session_state.onboarding_data['company_name'] = company_name
    st.session_state.onboarding_data['short_name'] = short_name

def render_onboarding_step2_branding():
    """Onboarding Step 2: Branding"""
    st.write("**Step 2: Newsletter Branding**")
    
    application_name = st.text_input("Application Name *",
                                     value=st.session_state.get('onboarding_data', {}).get('application_name', ''),
                                     help="What the newsletter will be called. Example: 'ACME Industry Newsletter'")
    newsletter_title_template = st.text_input("Newsletter Title Template",
                                             value=st.session_state.get('onboarding_data', {}).get('newsletter_title_template', '{name} - Week {week}'),
                                             help="Use {name} and {week} as placeholders")
    footer_text = st.text_input("Footer Text *",
                               value=st.session_state.get('onboarding_data', {}).get('footer_text', ''),
                               help="Text that appears at bottom of newsletters")
    footer_url = st.text_input("Footer URL *",
                              value=st.session_state.get('onboarding_data', {}).get('footer_url', ''),
                              help="Company website URL")
    footer_url_display = st.text_input("Footer URL Display Text",
                                       value=st.session_state.get('onboarding_data', {}).get('footer_url_display', ''),
                                       help="Display text for footer link. Example: 'www.acme.com'")
    
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}
    st.session_state.onboarding_data['application_name'] = application_name
    st.session_state.onboarding_data['newsletter_title_template'] = newsletter_title_template
    st.session_state.onboarding_data['footer_text'] = footer_text
    st.session_state.onboarding_data['footer_url'] = footer_url
    st.session_state.onboarding_data['footer_url_display'] = footer_url_display

def render_onboarding_step3_keywords():
    """Onboarding Step 3: Initial Keywords (Optional)"""
    st.write("**Step 3: Initial Keywords (Optional)**")
    st.info("You can add more keywords later. This step is optional.")
    
    if st.checkbox("Skip keywords for now", value=st.session_state.get('onboarding_data', {}).get('skip_keywords', False)):
        st.session_state.onboarding_data['skip_keywords'] = True
        st.session_state.onboarding_data['keywords'] = []
        return
    
    st.write("Keyword input interface - Coming soon")
    st.session_state.onboarding_data['keywords'] = []

def render_onboarding_step4_feeds():
    """Onboarding Step 4: Initial Feeds (Optional)"""
    st.write("**Step 4: Initial RSS Feeds (Optional)**")
    st.info("You can add more RSS feeds later. This step is optional.")
    
    if st.checkbox("Skip feeds for now", value=st.session_state.get('onboarding_data', {}).get('skip_feeds', False)):
        st.session_state.onboarding_data['skip_feeds'] = True
        st.session_state.onboarding_data['feeds'] = []
        return
    
    st.write("RSS feed input interface - Coming soon")
    st.session_state.onboarding_data['feeds'] = []

def render_onboarding_step5_contact():
    """Onboarding Step 5: Contact Information"""
    st.write("**Step 5: Contact & Subscription Information**")
    
    contact_name = st.text_input("Contact Name *",
                                 value=st.session_state.get('onboarding_data', {}).get('contact_name', ''))
    contact_email = st.text_input("Contact Email *",
                                value=st.session_state.get('onboarding_data', {}).get('contact_email', ''))
    phone = st.text_input("Phone Number",
                         value=st.session_state.get('onboarding_data', {}).get('phone', ''))
    subscription_tier = st.selectbox("Subscription Tier",
                                    ["Premium", "Standard", "Basic"],
                                    index=1,
                                    help="Determines user permissions")
    
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}
    st.session_state.onboarding_data['contact_name'] = contact_name
    st.session_state.onboarding_data['contact_email'] = contact_email
    st.session_state.onboarding_data['phone'] = phone
    st.session_state.onboarding_data['subscription_tier'] = subscription_tier

def render_onboarding_step6_review():
    """Onboarding Step 6: Review"""
    st.write("**Step 6: Review & Confirm**")
    
    data = st.session_state.get('onboarding_data', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Basic Information")
        st.write(f"**Customer ID:** {data.get('customer_id', 'N/A')}")
        st.write(f"**Company:** {data.get('company_name', 'N/A')}")
        st.write(f"**Short Name:** {data.get('short_name', 'N/A')}")
        
        st.subheader("Branding")
        st.write(f"**Application Name:** {data.get('application_name', 'N/A')}")
        st.write(f"**Title Template:** {data.get('newsletter_title_template', 'N/A')}")
        st.write(f"**Footer:** {data.get('footer_text', 'N/A')}")
        st.write(f"**Website:** {data.get('footer_url', 'N/A')}")
    
    with col2:
        st.subheader("Contact Information")
        st.write(f"**Name:** {data.get('contact_name', 'N/A')}")
        st.write(f"**Email:** {data.get('contact_email', 'N/A')}")
        st.write(f"**Phone:** {data.get('phone', 'N/A')}")
        st.write(f"**Tier:** {data.get('subscription_tier', 'N/A')}")
        
        st.subheader("Configuration")
        keywords_count = len(data.get('keywords', []))
        feeds_count = len(data.get('feeds', []))
        st.write(f"**Keywords:** {keywords_count}")
        st.write(f"**RSS Feeds:** {feeds_count}")
    
    st.info("Review all information above. You can go back to edit if needed.")

def render_onboarding_step7_create():
    """Onboarding Step 7: Create Customer Account"""
    st.write("**Step 7: Create Customer Account**")
    
    data = st.session_state.get('onboarding_data', {})
    
    st.success("Ready to create customer account!")
    st.write("Click 'Create Customer Account' below to:")
    st.write("1. Validate all information")
    st.write("2. Create customer folder in GitHub")
    st.write("3. Generate all configuration files")
    st.write("4. Add customer to system")
    
    if st.form_submit_button("✅ Create Customer Account", type="primary"):
        # TODO: Implement customer creation
        st.success(f"Customer account created for {data.get('company_name', 'Customer')}!")
        st.info("Customer account creation functionality will be implemented next.")
        # Reset form after creation
        # st.session_state.onboarding_step = 1
        # st.session_state.onboarding_data = {}

def render_config_viewer():
    """Configuration Viewer page"""
    st.header("Configuration Viewer")
    st.info("View and edit customer configurations - Coming soon")
    
    customer_selector = st.selectbox(
        "Select Customer",
        ["No customers available"],
        disabled=True
    )
    
    tab1, tab2, tab3 = st.tabs(["Keywords", "Feeds", "Branding"])
    
    with tab1:
        st.write("Keywords configuration will appear here")
    with tab2:
        st.write("RSS feeds configuration will appear here")
    with tab3:
        st.write("Branding configuration will appear here")

def render_activity_monitoring():
    """Activity Monitoring page"""
    st.header("Activity Monitoring")
    st.info("Monitor customer activities - Coming soon")
    
    customer_selector = st.selectbox(
        "Select Customer",
        ["No customers available"],
        disabled=True
    )
    
    tab1, tab2 = st.tabs(["Newsletters", "Articles"])
    
    with tab1:
        st.write("Newsletter activity will appear here")
    with tab2:
        st.write("Article finding activity will appear here")

def render_analytics():
    """Analytics page"""
    st.header("Analytics")
    st.info("Cross-customer analytics - Coming soon")
    
    tab1, tab2 = st.tabs(["Usage Patterns", "Trend Analysis"])
    
    with tab1:
        st.write("Usage patterns will appear here")
    with tab2:
        st.write("Trend analysis will appear here")

def render_export_import():
    """Export/Import page"""
    st.header("Export/Import")
    st.info("Export and import configurations - Coming soon")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Export")
        st.button("Export All Configs to Excel", disabled=True)
        st.button("Export Single Customer Config", disabled=True)
    
    with col2:
        st.subheader("Import")
        st.file_uploader("Upload Excel File", type=['xlsx'], disabled=True)
        st.button("Import Configs", disabled=True)

if __name__ == "__main__":
    main()

