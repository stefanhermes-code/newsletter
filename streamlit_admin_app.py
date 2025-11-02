"""
Admin Dashboard Application (GNP_Admin)

Multi-customer management dashboard for Newsletter Tool Cloud.
"""

import streamlit as st
from admin_modules import customer_manager
from admin_modules import config_viewer
from admin_modules import activity_monitor
from admin_modules import analytics_engine
from admin_modules import export_import
from admin_modules import admin_auth
from admin_modules.github_admin import list_all_customers

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
    # Check authentication
    if not admin_auth.check_admin_authentication():
        admin_auth.render_login_page()
        return
    
    # Show logout button in sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout", key="admin_logout"):
        admin_auth.logout_admin()
        return
    
    if st.session_state.get('admin_username'):
        st.sidebar.caption(f"Logged in as: **{st.session_state.admin_username}**")
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
    
    # Get customer stats
    all_customers = customer_manager.get_customer_list()
    active_customers = [c for c in all_customers if c.get("status", "").lower() == "active"]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(all_customers))
    with col2:
        st.metric("Active Customers", len(active_customers))
    with col3:
        st.metric("Total Newsletters", "N/A")  # TODO: Count newsletters from all customers
    with col4:
        st.metric("Pending Onboarding", "0")  # TODO: Track pending submissions
    
    st.markdown("---")
    
    # Recent customers
    if all_customers:
        st.subheader("Recent Customers")
        # Show last 5 customers (simple version - could sort by created_date)
        display_customers = all_customers[:5]
        for customer in display_customers:
            st.write(f"**{customer.get('company_name', customer.get('customer_id'))}** - {customer.get('status', 'Unknown')}")
    else:
        st.info("No customers yet. Use 'Customer Onboarding' to create your first customer.")

def render_customer_management():
    """Customer Management page"""
    st.header("Customer Management")
    
    tab1, tab2, tab3 = st.tabs(["Customer List", "Customer Details", "User Access Management"])
    
    with tab1:
        st.subheader("All Customers")
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input("Search Customers", placeholder="Search by name, ID, or email", key="customer_search")
        with col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "Inactive"], key="status_filter")
        
        # Get filtered customers
        if search_query:
            customers = customer_manager.search_customers(search_query)
        else:
            customers = customer_manager.filter_customers(status_filter)
        
        if customers:
            st.write(f"**{len(customers)} customer(s) found**")
            
            for customer in customers:
                with st.expander(f"**{customer.get('company_name', customer.get('customer_id'))}** ({customer.get('customer_id')})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Status:** {customer.get('status', 'Unknown')}")
                        st.write(f"**ID:** {customer.get('customer_id')}")
                    with col2:
                        contact_email = customer.get('contact_email', 'N/A')
                        st.write(f"**Contact:** {contact_email}")
                        st.write(f"**Tier:** {customer.get('subscription_tier', 'N/A')}")
                    with col3:
                        if st.button(f"View Details", key=f"view_{customer.get('customer_id')}"):
                            st.session_state.selected_customer_id = customer.get('customer_id')
                            st.session_state.customer_management_tab = "Customer Details"
                            st.rerun()
                        if st.button(f"Manage Users", key=f"users_{customer.get('customer_id')}"):
                            st.session_state.selected_customer_id = customer.get('customer_id')
                            st.session_state.customer_management_tab = "User Access Management"
                            st.rerun()
        else:
            st.info("No customers found. Use 'Customer Onboarding' to create your first customer.")
    
    with tab2:
        st.subheader("Customer Details")
        
        # Customer selector
        all_customer_ids = ["-- Select Customer --"] + list_all_customers()
        selected_id = st.selectbox(
            "Select Customer",
            all_customer_ids,
            index=0 if st.session_state.get('selected_customer_id') not in all_customer_ids 
                   else all_customer_ids.index(st.session_state.get('selected_customer_id'))
        )
        
        if selected_id != "-- Select Customer --":
            st.session_state.selected_customer_id = selected_id
            details = customer_manager.get_customer_details(selected_id)
            
            if details:
                # Display customer info
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Basic Information**")
                    st.write(f"Customer ID: {details['customer_id']}")
                    st.write(f"Company: {details['info'].get('company_name', 'N/A')}")
                    st.write(f"Status: {details['info'].get('status', 'Unknown')}")
                    st.write(f"Created: {details['info'].get('created_date', 'N/A')}")
                
                with col2:
                    st.write("**Contact Information**")
                    st.write(f"Name: {details['info'].get('contact_name', 'N/A')}")
                    st.write(f"Email: {details['info'].get('contact_email', 'N/A')}")
                    st.write(f"Phone: {details['info'].get('phone', 'N/A')}")
                    st.write(f"Tier: {details['info'].get('subscription_tier', 'N/A')}")
                
                st.markdown("---")
                
                # Configuration summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    keywords_count = len(details['keywords'].get('keywords', []))
                    st.metric("Keywords", keywords_count)
                with col2:
                    feeds_count = len(details['feeds'].get('feeds', []))
                    st.metric("RSS Feeds", feeds_count)
                with col3:
                    users_count = len(details['user_access'].get('users', []))
                    st.metric("Users", users_count)
            else:
                st.error("Failed to load customer details")
    
    with tab3:
        st.subheader("User Access Management")
        
        # Customer selector
        all_customer_ids = ["-- Select Customer --"] + list_all_customers()
        selected_id = st.selectbox(
            "Select Customer",
            all_customer_ids,
            key="user_access_customer_selector"
        )
        
        if selected_id != "-- Select Customer --":
            # Get users
            users = customer_manager.get_user_access_list(selected_id)
            
            if users:
                st.write(f"**{len(users)} user(s) with access**")
                
                for user in users:
                    with st.expander(f"**{user.get('email')}** - {user.get('tier', 'N/A').title()}"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Tier:** {user.get('tier', 'N/A')}")
                            st.write(f"**Role:** {user.get('role', 'N/A')}")
                        with col2:
                            st.write(f"**Status:** {user.get('status', 'Active')}")
                            st.write(f"**Valid Until:** {user.get('valid_until', 'No expiry')}")
                        with col3:
                            new_tier = st.selectbox(
                                "Change Tier",
                                ["Premium", "Standard", "Basic"],
                                index=["premium", "standard", "basic"].index(user.get('tier', 'basic').lower()) if user.get('tier', 'basic').lower() in ["premium", "standard", "basic"] else 1,
                                key=f"tier_{user.get('email')}"
                            )
                            if new_tier.lower() != user.get('tier', '').lower():
                                if st.button("Update Tier", key=f"update_tier_{user.get('email')}"):
                                    if customer_manager.update_user_tier(selected_id, user.get('email'), new_tier):
                                        st.success("Tier updated!")
                                        st.rerun()
                            
                            if st.button("Remove User", key=f"remove_{user.get('email')}"):
                                if customer_manager.remove_user_access(selected_id, user.get('email')):
                                    st.success("User removed!")
                                    st.rerun()
            else:
                st.info("No users found for this customer.")
            
            # Add new user
            st.markdown("---")
            st.subheader("Add New User")
            with st.form("add_user_form"):
                new_email = st.text_input("Email Address", key="new_user_email")
                new_tier = st.selectbox("Tier", ["Premium", "Standard", "Basic"], key="new_user_tier")
                new_role = st.selectbox("Role", ["admin", "editor", "viewer"], key="new_user_role")
                new_password = st.text_input("Initial Password", type="password", value="changeme123", key="new_user_password")
                
                if st.form_submit_button("Add User"):
                    if new_email:
                        if customer_manager.add_user_access(selected_id, new_email, new_tier, new_role, new_password):
                            st.success(f"User {new_email} added!")
                            st.rerun()
                    else:
                        st.error("Email address is required")

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
    
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}
    
    if st.checkbox("Skip keywords for now", value=st.session_state.onboarding_data.get('skip_keywords', False), key="skip_keywords_check"):
        st.session_state.onboarding_data['skip_keywords'] = True
        st.session_state.onboarding_data['keywords'] = []
        return
    
    st.session_state.onboarding_data['skip_keywords'] = False
    
    # Load existing keywords if any
    existing_keywords = st.session_state.onboarding_data.get('keywords', [])
    
    st.write("**Add Keywords:**")
    new_keyword = st.text_input("Enter keyword", key="new_keyword_input_step3")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("➕ Add", key="add_keyword_step3"):
            if new_keyword and new_keyword.strip():
                if new_keyword.strip().lower() not in [k.lower() for k in existing_keywords]:
                    existing_keywords.append(new_keyword.strip())
                    st.session_state.onboarding_data['keywords'] = existing_keywords
                    st.rerun()
                else:
                    st.warning("Keyword already added")
    
    # Display keywords
    if existing_keywords:
        st.write("**Current Keywords:**")
        cols = st.columns(min(len(existing_keywords), 4))
        for idx, keyword in enumerate(existing_keywords):
            with cols[idx % len(cols)]:
                col_del, col_kw = st.columns([1, 4])
                with col_kw:
                    st.write(f"• {keyword}")
                with col_del:
                    if st.button("🗑️", key=f"del_kw_{idx}"):
                        existing_keywords.remove(keyword)
                        st.session_state.onboarding_data['keywords'] = existing_keywords
                        st.rerun()
    
    st.session_state.onboarding_data['keywords'] = existing_keywords

def render_onboarding_step4_feeds():
    """Onboarding Step 4: Initial Feeds (Optional)"""
    st.write("**Step 4: Initial RSS Feeds (Optional)**")
    st.info("You can add more RSS feeds later. This step is optional.")
    
    if 'onboarding_data' not in st.session_state:
        st.session_state.onboarding_data = {}
    
    if st.checkbox("Skip feeds for now", value=st.session_state.onboarding_data.get('skip_feeds', False), key="skip_feeds_check"):
        st.session_state.onboarding_data['skip_feeds'] = True
        st.session_state.onboarding_data['feeds'] = []
        return
    
    st.session_state.onboarding_data['skip_feeds'] = False
    
    # Load existing feeds if any
    existing_feeds = st.session_state.onboarding_data.get('feeds', [])
    
    st.write("**Add RSS Feed:**")
    col1, col2 = st.columns(2)
    with col1:
        feed_name = st.text_input("Feed Name", key="new_feed_name_step4")
    with col2:
        feed_url = st.text_input("Feed URL", key="new_feed_url_step4", placeholder="https://example.com/rss")
    
    if st.button("➕ Add Feed", key="add_feed_step4"):
        if feed_name and feed_url:
            if feed_url.startswith(("http://", "https://")):
                # Check for duplicates
                if not any(f.get('url', '').lower() == feed_url.lower() for f in existing_feeds):
                    existing_feeds.append({
                        "name": feed_name,
                        "url": feed_url,
                        "enabled": True
                    })
                    st.session_state.onboarding_data['feeds'] = existing_feeds
                    st.rerun()
                else:
                    st.warning("Feed URL already added")
            else:
                st.error("Feed URL must start with http:// or https://")
        else:
            st.warning("Please enter both name and URL")
    
    # Display feeds
    if existing_feeds:
        st.write("**Current Feeds:**")
        for idx, feed in enumerate(existing_feeds):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{feed.get('name')}**")
            with col2:
                st.caption(f"🔗 {feed.get('url')}")
            with col3:
                if st.button("🗑️ Delete", key=f"del_feed_{idx}"):
                    existing_feeds.remove(feed)
                    st.session_state.onboarding_data['feeds'] = existing_feeds
                    st.rerun()
    
    st.session_state.onboarding_data['feeds'] = existing_feeds

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
    
    # Validation
    required_fields = ['customer_id', 'company_name', 'short_name', 'application_name', 
                      'footer_text', 'footer_url', 'contact_name', 'contact_email', 'subscription_tier']
    
    missing_fields = [field for field in required_fields if not data.get(field)]
    
    if missing_fields:
        st.warning(f"⚠️ Please complete all required fields before creating account. Missing: {', '.join(missing_fields)}")
        st.info("Go back to previous steps to fill in required information.")
        return
    
    st.success("✅ All information validated!")
    st.write("Click 'Create Customer Account' below to:")
    st.write("1. ✅ Validate all information")
    st.write("2. Create customer folder in GitHub")
    st.write("3. Generate all configuration files")
    st.write("4. Create initial user account")
    st.write("5. Add customer to system")
    
    # Initial password field
    initial_password = st.text_input(
        "Initial Password for Contact Email",
        value=data.get('initial_password', 'changeme123'),
        type="password",
        help="This will be the initial password for the contact email. User can change it later."
    )
    
    if st.form_submit_button("✅ Create Customer Account", type="primary"):
        with st.spinner("Creating customer account..."):
            # Prepare customer data
            customer_data = {
                "customer_id": data.get('customer_id'),
                "company_name": data.get('company_name'),
                "short_name": data.get('short_name'),
                "application_name": data.get('application_name'),
                "newsletter_title_template": data.get('newsletter_title_template', '{name} - Week {week}'),
                "footer_text": data.get('footer_text'),
                "footer_url": data.get('footer_url'),
                "footer_url_display": data.get('footer_url_display', data.get('footer_url', '')),
                "contact_name": data.get('contact_name'),
                "contact_email": data.get('contact_email'),
                "phone": data.get('phone', ''),
                "subscription_tier": data.get('subscription_tier', 'Standard'),
                "initial_password": initial_password,
                "keywords": data.get('keywords', []),
                "feeds": data.get('feeds', [])
            }
            
            # Create customer
            success = customer_manager.create_customer_record(customer_data)
            
            if success:
                st.success(f"🎉 Customer account created successfully for {data.get('company_name')}!")
                st.info(f"**Customer ID:** {data.get('customer_id')}")
                st.info(f"**Initial User:** {data.get('contact_email')} (Password: {initial_password})")
                st.info("User can now log in to the User App and change their password.")
                
                # Reset form
                st.session_state.onboarding_step = 1
                st.session_state.onboarding_data = {}
                st.balloons()
                st.rerun()
            else:
                st.error("Failed to create customer account. Please check the error messages above and try again.")

def render_config_viewer():
    """Configuration Viewer page"""
    config_viewer.render_config_viewer()

def render_activity_monitoring():
    """Activity Monitoring page"""
    activity_monitor.render_activity_monitoring()

def render_analytics():
    """Analytics page"""
    analytics_engine.render_analytics()

def render_export_import():
    """Export/Import page"""
    export_import.render_export_import()

if __name__ == "__main__":
    main()

