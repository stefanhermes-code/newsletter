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
                sidebar_logo_found = True
                break
            except Exception as e:
                continue
    if not sidebar_logo_found:
        # Try to display anyway (might work on Streamlit Cloud from GitHub)
        for path in sidebar_logo_paths:
            try:
                st.sidebar.image(path, width=150)  # Smaller width for sidebar
                break
            except:
                continue
    
    # Logout button directly after logo (matching User App layout)
    if st.sidebar.button("🚪 Logout", key="admin_logout"):
        admin_auth.logout_admin()
        return
    
    if st.session_state.get('admin_username'):
        st.sidebar.caption(f"Logged in as: **{st.session_state.admin_username}**")
    
    st.sidebar.markdown("---")
    
    # Navigation title with emoji (matching User App style)
    st.sidebar.title("🧭 Navigation")
    
    # Navigation options
    nav_options = [
        "Overview",
        "Customer Management",
        "Customer Onboarding",
        "Configuration Viewer",
        "Activity Monitoring",
        "Analytics",
        "Export/Import"
    ]
    
    # Simple: get page from session state, default to Overview
    if 'current_admin_page' not in st.session_state:
        st.session_state.current_admin_page = "Overview"
    
    # Render selectbox - it will update session state when changed
    selected_page = st.sidebar.selectbox(
        "Select page",
        nav_options,
        index=nav_options.index(st.session_state.current_admin_page),
        key="admin_nav_selectbox",
        label_visibility="collapsed"  # Hide label for consistency with User App
    )
    
    # Update session state if user changed selectbox (selectbox drives navigation)
    if selected_page != st.session_state.current_admin_page:
        st.session_state.current_admin_page = selected_page
    
    # Use session state as source of truth
    page = st.session_state.current_admin_page
    
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
    
    # Count newsletters from all customers (same logic as Activity Monitoring)
    from admin_modules.github_admin import list_customer_files
    total_newsletters = 0
    for customer in all_customers:
        customer_id = customer.get("customer_id")
        if customer_id:
            newsletters = list_customer_files(customer_id, "data/newsletters")
            newsletter_count = len([f for f in newsletters if f.get('name', '').endswith('.html')])
            total_newsletters += newsletter_count
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", len(all_customers))
    with col2:
        st.metric("Active Customers", len(active_customers))
    with col3:
        st.metric("Total Newsletters", total_newsletters)
    with col4:
        st.metric("Pending Onboarding", "0")  # Removed - not needed (see onboarding simplification)
    
    st.markdown("---")
    
    # Recent customers
    if all_customers:
        st.subheader("Recent Customers")
        # Show last 5 customers (simple version - could sort by created_date)
        display_customers = all_customers[:5]
        for customer in display_customers:
            st.write(f"**{customer.get('company_name', customer.get('customer_id'))}** - {customer.get('status', 'Unknown')}")
    else:
        st.info("No customers yet. Go to 'Customer Onboarding' in the sidebar to create your first customer.")

def render_customer_management():
    """Customer Management page"""
    st.header("Customer Management")
    
    # Initialize tab state
    if 'customer_management_tab' not in st.session_state:
        st.session_state.customer_management_tab = "Customer List"
    
    # Get requested tab (from button click or existing state)
    requested_tab = st.session_state.get('customer_management_tab', "Customer List")
    tab_options = ["Customer List", "Customer Details", "User Access Management"]
    
    # Calculate index for radio button
    if requested_tab in tab_options:
        default_index = tab_options.index(requested_tab)
    else:
        default_index = 0
    
    # Tab selector (allows programmatic switching via buttons)
    selected_tab = st.radio(
        "View",
        tab_options,
        horizontal=True,
        key="customer_mgmt_tab_selector",
        index=default_index
    )
    
    # Update session state with selected tab
    st.session_state.customer_management_tab = selected_tab
    
    # Render appropriate view
    if selected_tab == "Customer List":
        tab1 = True
        tab2 = False
        tab3 = False
    elif selected_tab == "Customer Details":
        tab1 = False
        tab2 = True
        tab3 = False
    else:  # User Access Management
        tab1 = False
        tab2 = False
        tab3 = True
    
    if tab1:
        st.subheader("All Customers")
        
        st.markdown("---")
        
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
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Status:** {customer.get('status', 'Unknown')}")
                        st.write(f"**ID:** {customer.get('customer_id')}")
                    with col2:
                        contact_email = customer.get('contact_email', 'N/A')
                        st.write(f"**Contact:** {contact_email}")
                        st.write(f"**Tier:** {customer.get('subscription_tier', 'N/A')}")
        else:
            st.info("No customers found. Use 'Customer Onboarding' to create your first customer.")
    
    if tab2:
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
                # Display header with customer logo (matching User App style)
                branding = details.get('branding', {})
                logo_path = branding.get('logo_path', '')
                app_name = branding.get('application_name', 'Newsletter')
                company_name = details.get('info', {}).get('company_name', selected_id)
                
                if logo_path:
                    try:
                        col_logo, col_title = st.columns([1, 4])
                        with col_logo:
                            st.image(logo_path, width=150)
                        with col_title:
                            st.title(f"👥 Customer Details - {app_name}")
                    except:
                        st.title(f"👥 Customer Details - {company_name}")
                else:
                    st.title(f"👥 Customer Details - {company_name}")
                
                st.markdown("---")
                
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
                
                st.markdown("---")
                
                # Customer management actions
                st.subheader("Customer Management Actions")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Change status (Active/Inactive)
                    current_status = details['info'].get('status', 'Active')
                    new_status = st.selectbox(
                        "Customer Status",
                        ["Active", "Inactive"],
                        index=0 if current_status.lower() == "active" else 1,
                        key=f"status_select_{selected_id}"
                    )
                    if new_status != current_status:
                        if st.button(f"💾 Update Status to {new_status}", key=f"update_status_{selected_id}"):
                            # Update customer info with new status
                            from admin_modules.github_admin import update_customer_info
                            updated_info = details['info'].copy()
                            updated_info['status'] = new_status
                            if update_customer_info(selected_id, updated_info, f"Change customer status to {new_status}"):
                                st.success(f"Customer status updated to {new_status}")
                                st.rerun()
                            else:
                                st.error("Failed to update customer status")
                
                with col2:
                    # Delete customer (dangerous action)
                    st.warning("⚠️ **Danger Zone**")
                    if st.button("🗑️ Delete Customer", key=f"delete_customer_{selected_id}", type="secondary"):
                        st.error("⚠️ Customer deletion is not yet implemented. To delete a customer, manually remove their folder from GitHub repository.")
                        # TODO: Implement customer deletion (requires deleting entire folder from GitHub)
            else:
                st.error("Failed to load customer details")
    
    if tab3:
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
    """Customer Onboarding page - Simplified to minimum required fields"""
    st.header("Customer Onboarding")
    
    st.info("**Simplified Onboarding:** This creates a customer account with minimum required information. "
            "After creation, users can configure keywords, RSS feeds, and branding themselves via the User App Configuration page.")
    
    st.markdown("---")
    
    with st.form("simplified_onboarding_form"):
        st.subheader("Required Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            customer_id = st.text_input(
                "Customer ID *",
                help="Lowercase, alphanumeric only. Example: 'acme', 'htc', 'apba'",
                placeholder="e.g., acme"
            )
            company_name = st.text_input(
                "Company Name *",
                placeholder="e.g., ACME Corporation"
            )
            contact_email = st.text_input(
                "Contact Email *",
                help="This email will become the login account",
                placeholder="user@company.com"
            )
        
        with col2:
            subscription_tier = st.selectbox(
                "Subscription Tier *",
                ["Premium", "Standard", "Basic"],
                index=1,
                help="Determines user permissions: Premium=full access, Standard=view+generate, Basic=view only"
            )
            initial_password = st.text_input(
                "Initial Password *",
                type="password",
                value="changeme123",
                help="Initial password for the contact email. User should change this after first login."
            )
            contact_name = st.text_input(
                "Contact Name (Optional)",
                placeholder="e.g., John Doe"
            )
        
        st.markdown("---")
        
        st.subheader("Optional Information")
        st.caption("These can be configured later by the user via the User App Configuration page.")
        
        short_name = st.text_input(
            "Short Name (Optional)",
            help="Used in file names. Defaults to Customer ID if not provided.",
            placeholder="e.g., ACME"
        )
        
        st.markdown("---")
        
        submitted = st.form_submit_button("✅ Create Customer Account", type="primary")
        
        if submitted:
            # Validate required fields
            from admin_modules.validators import validate_customer_id, validate_required_field, validate_email
            
            errors = []
            
            # Validate customer ID
            customer_id_clean = customer_id.strip().lower() if customer_id else ""
            is_valid_id, id_error = validate_customer_id(customer_id_clean)
            if not is_valid_id:
                errors.append(id_error)
            
            # Validate company name
            company_name_clean = company_name.strip() if company_name else ""
            is_valid_company, company_error = validate_required_field(company_name_clean, "Company Name")
            if not is_valid_company:
                errors.append(company_error)
            
            # Validate contact email
            contact_email_clean = contact_email.strip().lower() if contact_email else ""
            is_valid_email, email_error = validate_email(contact_email_clean)
            if not is_valid_email:
                errors.append(email_error)
            
            # Validate password
            if not initial_password or not initial_password.strip():
                errors.append("Initial Password is required")
            
            # Check if customer ID already exists
            if customer_id_clean:
                from admin_modules.github_admin import list_all_customers
                existing_customers = list_all_customers()
                if customer_id_clean in existing_customers:
                    errors.append(f"Customer ID '{customer_id_clean}' already exists. Please choose a different ID.")
            
            if errors:
                for error in errors:
                    st.error(error)
                st.stop()
            
            # Prepare customer data with defaults
            customer_data = {
                "customer_id": customer_id_clean,
                "company_name": company_name_clean,
                "short_name": short_name.strip() if short_name and short_name.strip() else customer_id_clean.upper(),
                "application_name": f"{company_name_clean} Newsletter",  # Default application name
                "newsletter_title_template": "{name} - Week {week}",  # Default template
                "footer_text": "",  # Empty - user can add later
                "footer_url": "",  # Empty - user can add later
                "footer_url_display": "",  # Empty - user can add later
                "contact_name": contact_name.strip() if contact_name else "",
                "contact_email": contact_email_clean,
                "phone": "",  # Empty - user can add later
                "subscription_tier": subscription_tier,
                "initial_password": initial_password,
                "keywords": [],  # Empty - user can add via Configuration page
                "feeds": []  # Empty - user can add via Configuration page
            }
            
            # Create customer
            with st.spinner("Creating customer account..."):
                from admin_modules import customer_manager
                success = customer_manager.create_customer_record(customer_data)
                
                if success:
                    st.success(f"🎉 Customer account created successfully!")
                    st.info(f"**Customer ID:** {customer_id_clean}")
                    st.info(f"**Company:** {company_name_clean}")
                    st.info(f"**Initial User:** {contact_email_clean}")
                    st.info(f"**Initial Password:** {initial_password}")
                    st.info(f"**Subscription Tier:** {subscription_tier}")
                    st.success("✅ User can now log in to the User App and:")
                    st.write("- Change their password (Configuration → Change Password)")
                    st.write("- Add keywords (Configuration → Keywords)")
                    st.write("- Add RSS feeds (Configuration → RSS Feeds)")
                    st.write("- Configure branding (Configuration → Branding, if Premium tier)")
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create customer account. Please check the error messages above and try again.")

# Old onboarding step functions removed - using simplified single-form onboarding above

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

