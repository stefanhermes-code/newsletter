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
from datetime import datetime

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
                    st.caption("This will permanently remove the customer's data folder from the repository. This action cannot be undone.")
                    confirm_text = st.text_input(
                        "Type the Customer ID to confirm deletion",
                        key=f"confirm_delete_{selected_id}"
                    )
                    confirm_checkbox = st.checkbox(
                        "I understand this action is irreversible",
                        key=f"confirm_delete_chk_{selected_id}"
                    )
                    delete_disabled = not (confirm_checkbox and confirm_text.strip().lower() == selected_id.strip().lower())
                    if st.button("🗑️ Permanently Delete Customer", key=f"delete_customer_{selected_id}", type="secondary", disabled=delete_disabled):
                        from admin_modules.github_admin import delete_customer
                        with st.spinner("Deleting customer..."):
                            if delete_customer(selected_id):
                                st.success("Customer deleted successfully")
                                st.rerun()
                            else:
                                st.error("Failed to delete customer")
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
                    # Generate customer onboarding document and store in session state
                    onboarding_html = generate_customer_onboarding_document(
                        customer_id=customer_id_clean,
                        company_name=company_name_clean,
                        contact_name=contact_name.strip() if contact_name else "",
                        contact_email=contact_email_clean,
                        initial_password=initial_password,
                        subscription_tier=subscription_tier,
                        short_name=short_name.strip() if short_name and short_name.strip() else customer_id_clean.upper()
                    )
                    
                    # Store in session state for display outside form
                    st.session_state.onboarding_document_html = onboarding_html
                    st.session_state.onboarding_document_filename = f"Customer_Onboarding_{customer_id_clean}_{datetime.now().strftime('%Y%m%d')}.html"
                    st.session_state.onboarding_customer_id = customer_id_clean
                    st.session_state.onboarding_company_name = company_name_clean
                    st.session_state.onboarding_contact_email = contact_email_clean
                    st.session_state.onboarding_subscription_tier = subscription_tier
                    st.session_state.onboarding_success = True
                    
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Failed to create customer account. Please check the error messages above and try again.")
    
    # Display success message and document outside the form (after form submission)
    if st.session_state.get("onboarding_success", False):
        st.markdown("---")
        st.success(f"🎉 Customer account created successfully!")
        
        # Display summary
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"**Customer ID:** {st.session_state.onboarding_customer_id}")
            st.info(f"**Company:** {st.session_state.get('onboarding_company_name', 'N/A')}")
            st.info(f"**Initial User:** {st.session_state.get('onboarding_contact_email', 'N/A')}")
            st.info(f"**Subscription Tier:** {st.session_state.get('onboarding_subscription_tier', 'N/A')}")
        
        with col2:
            st.success("✅ User can now log in to the User App and:")
            st.write("- Change their password (Configuration → Change Password)")
            st.write("- Add keywords (Configuration → Keywords)")
            st.write("- Add RSS feeds (Configuration → RSS Feeds)")
            st.write("- Configure branding (Configuration → Branding, if Premium tier)")
        
        st.markdown("---")
        
        # Display and download onboarding document (outside form)
        st.subheader("📄 Customer Onboarding Document")
        st.info("This document contains all the customer's account details. You can download it to send to the customer.")
        
        # Preview the document
        st.markdown("### Document Preview")
        if "onboarding_document_html" in st.session_state:
            st.components.v1.html(st.session_state.onboarding_document_html, height=600, scrolling=True)
            
            # Download button (outside form)
            st.download_button(
                label="📥 Download Customer Onboarding Document",
                data=st.session_state.onboarding_document_html,
                file_name=st.session_state.onboarding_document_filename,
                mime="text/html",
                key="download_onboarding_doc",
                type="primary"
            )
        
        # Clear success flag after displaying
        if st.button("Create Another Customer", key="create_another"):
            st.session_state.onboarding_success = False
            st.session_state.onboarding_document_html = None
            st.session_state.onboarding_document_filename = None
            st.session_state.onboarding_customer_id = None
            st.rerun()

# Old onboarding step functions removed - using simplified single-form onboarding above

def generate_customer_onboarding_document(customer_id: str, company_name: str, contact_name: str,
                                         contact_email: str, initial_password: str, 
                                         subscription_tier: str, short_name: str) -> str:
    """
    Generate HTML document with customer onboarding details
    
    Args:
        customer_id: Customer identifier
        company_name: Company name
        contact_name: Contact person name
        contact_email: Contact email (login)
        initial_password: Initial password
        subscription_tier: Subscription tier (Premium/Standard/Basic)
        short_name: Short name for company
    
    Returns:
        HTML string with onboarding information
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    
    # Tier permissions description
    tier_descriptions = {
        "Premium": "Full access to all features including configuration editing",
        "Standard": "View newsletters and generate new ones",
        "Basic": "View newsletters only"
    }
    
    tier_description = tier_descriptions.get(subscription_tier, subscription_tier)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Customer Onboarding - {company_name}</title>
    <style>
        @page {{ margin: 2cm; size: A4; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .document-container {{
            background-color: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #2c5aa0;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c5aa0;
            margin: 0;
            font-size: 28px;
        }}
        .header .date {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            color: #2c5aa0;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 5px;
        }}
        .info-row {{
            display: flex;
            margin-bottom: 12px;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        .info-label {{
            font-weight: bold;
            color: #555;
            width: 200px;
            flex-shrink: 0;
        }}
        .info-value {{
            color: #333;
            flex-grow: 1;
        }}
        .credentials-box {{
            background-color: #f8f9fa;
            border-left: 4px solid #2c5aa0;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .credentials-box .label {{
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 5px;
        }}
        .credentials-box .value {{
            font-family: 'Courier New', monospace;
            font-size: 16px;
            color: #333;
            padding: 5px;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 3px;
        }}
        .instructions {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .instructions h3 {{
            color: #2c5aa0;
            margin-top: 0;
        }}
        .instructions ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        .instructions li {{
            margin: 8px 0;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            font-size: 12px;
            color: #666;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .warning strong {{
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="document-container">
        <div class="header">
            <h1>Welcome to GlobalNewsPilot Newsletter Tool</h1>
            <div class="date">Account Created: {current_date}</div>
        </div>
        
        <div class="section">
            <div class="section-title">Account Information</div>
            <div class="info-row">
                <div class="info-label">Company Name:</div>
                <div class="info-value">{company_name}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Customer ID:</div>
                <div class="info-value">{customer_id}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Short Name:</div>
                <div class="info-value">{short_name}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Subscription Tier:</div>
                <div class="info-value"><strong>{subscription_tier}</strong> - {tier_description}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Login Credentials</div>
            <div class="credentials-box">
                <div class="label">Email Address (Username):</div>
                <div class="value">{contact_email}</div>
            </div>
            <div class="credentials-box">
                <div class="label">Initial Password:</div>
                <div class="value">{initial_password}</div>
            </div>
            <div class="warning">
                <strong>⚠️ Important:</strong> Please change your password immediately after your first login for security purposes.
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Contact Information</div>
            <div class="info-row">
                <div class="info-label">Contact Name:</div>
                <div class="info-value">{contact_name if contact_name else "Not provided"}</div>
            </div>
            <div class="info-row">
                <div class="info-label">Contact Email:</div>
                <div class="info-value">{contact_email}</div>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Getting Started</div>
            <div class="instructions">
                <h3>Next Steps:</h3>
                <ul>
                    <li><strong>Log in</strong> to the User App using your email and initial password</li>
                    <li><strong>Change your password</strong> (Configuration → Change Password tab)</li>
                    <li><strong>Add keywords</strong> for news searching (Configuration → Keywords tab)</li>
                    <li><strong>Add RSS feeds</strong> (optional, Configuration → RSS Feeds tab)</li>
                    <li><strong>Configure branding</strong> (Configuration → Branding tab, if Premium tier)</li>
                    <li><strong>Start generating newsletters</strong> from the Dashboard</li>
                </ul>
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">Account Features</div>
            <div class="instructions">
                <h3>What you can do with your account:</h3>
                <ul>
                    <li><strong>Find News:</strong> Search for articles based on your configured keywords</li>
                    <li><strong>Generate Newsletters:</strong> Create professional HTML newsletters from selected articles</li>
                    <li><strong>View Newsletters:</strong> Access all your generated newsletters</li>
                    <li><strong>Manage Configuration:</strong> Update keywords, RSS feeds, and branding settings</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>GlobalNewsPilot Newsletter Tool</strong></p>
            <p>For support or questions, please contact your administrator.</p>
            <p>Document generated on {current_date}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

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

