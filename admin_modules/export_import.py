"""
Export/Import Module

Export and import customer configurations to/from Excel files.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Optional
from admin_modules.github_admin import list_all_customers
from admin_modules.customer_manager import get_customer_details, update_customer_info_admin
from admin_modules.github_admin import update_customer_config
from datetime import datetime
import io

def render_export_import():
    """Render export/import interface"""
    st.header("Export/Import")
    
    col1, col2 = st.columns(2)
    
    with col1:
        render_export()
    
    with col2:
        render_import()

def render_export():
    """Render export functionality"""
    st.subheader("Export Configurations")
    
    all_customers = list_all_customers()
    
    if not all_customers:
        st.info("No customers to export.")
        return
    
    export_option = st.radio(
        "Export Option",
        ["All Customers", "Single Customer"],
        key="export_option"
    )
    
    if export_option == "All Customers":
        if st.button("📥 Export All Configs to Excel", type="primary"):
            with st.spinner("Exporting all configurations..."):
                excel_data = export_all_configs_to_excel()
                if excel_data:
                    st.success("Export complete!")
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_data,
                        file_name=f"all_customer_configs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
    else:
        selected_customer = st.selectbox(
            "Select Customer",
            ["-- Select --"] + all_customers,
            key="export_customer_selector"
        )
        
        if selected_customer != "-- Select --":
            if st.button("📥 Export Customer Config", type="primary"):
                with st.spinner("Exporting customer configuration..."):
                    excel_data = export_customer_configs(selected_customer)
                    if excel_data:
                        st.success("Export complete!")
                        st.download_button(
                            label="📥 Download Excel File",
                            data=excel_data,
                            file_name=f"{selected_customer}_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

def render_import():
    """Render import functionality"""
    st.subheader("Import Configurations")
    
    uploaded_file = st.file_uploader(
        "Upload Excel File",
        type=['xlsx'],
        key="import_file_uploader"
    )
    
    if uploaded_file:
        st.info("File uploaded. Review and import below.")
        
        try:
            # Read Excel file
            df = pd.read_excel(uploaded_file)
            st.dataframe(df.head(20))  # Preview first 20 rows
            
            if st.button("📤 Import Configs", type="primary"):
                with st.spinner("Importing configurations..."):
                    result = import_configs_from_excel(uploaded_file)
                    if result['success']:
                        st.success(f"Successfully imported {result['count']} configuration(s)!")
                        if result['errors']:
                            st.warning(f"Some errors occurred: {result['errors']}")
                    else:
                        st.error(f"Import failed: {result.get('error', 'Unknown error')}")
        except Exception as e:
            st.error(f"Error reading Excel file: {str(e)}")

def export_all_configs_to_excel() -> Optional[bytes]:
    """
    Export all customer configurations to Excel
    
    Returns:
        Excel file as bytes, or None if error
    """
    try:
        all_customers = list_all_customers()
        
        # Create Excel writer
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Customer Info
            customer_data = []
            for customer_id in all_customers:
                details = get_customer_details(customer_id)
                if details:
                    info = details.get('info', {})
                    customer_data.append({
                        'Customer ID': customer_id,
                        'Company Name': info.get('company_name', ''),
                        'Status': info.get('status', ''),
                        'Contact Name': info.get('contact_name', ''),
                        'Contact Email': info.get('contact_email', ''),
                        'Phone': info.get('phone', ''),
                        'Subscription Tier': info.get('subscription_tier', ''),
                        'Created Date': info.get('created_date', '')
                    })
            
            if customer_data:
                df_customers = pd.DataFrame(customer_data)
                df_customers.to_excel(writer, sheet_name='Customers', index=False)
            
            # Sheet 2: Keywords (one row per keyword)
            keywords_data = []
            for customer_id in all_customers:
                details = get_customer_details(customer_id)
                if details:
                    keywords = details.get('keywords', {}).get('keywords', [])
                    for keyword in keywords:
                        keywords_data.append({
                            'Customer ID': customer_id,
                            'Keyword': keyword
                        })
            
            if keywords_data:
                df_keywords = pd.DataFrame(keywords_data)
                df_keywords.to_excel(writer, sheet_name='Keywords', index=False)
            
            # Sheet 3: RSS Feeds
            feeds_data = []
            for customer_id in all_customers:
                details = get_customer_details(customer_id)
                if details:
                    feeds = details.get('feeds', {}).get('feeds', [])
                    for feed in feeds:
                        feeds_data.append({
                            'Customer ID': customer_id,
                            'Feed Name': feed.get('name', ''),
                            'Feed URL': feed.get('url', ''),
                            'Enabled': feed.get('enabled', True)
                        })
            
            if feeds_data:
                df_feeds = pd.DataFrame(feeds_data)
                df_feeds.to_excel(writer, sheet_name='RSS Feeds', index=False)
            
            # Sheet 4: Branding
            branding_data = []
            for customer_id in all_customers:
                details = get_customer_details(customer_id)
                if details:
                    branding = details.get('branding', {})
                    branding_data.append({
                        'Customer ID': customer_id,
                        'Application Name': branding.get('application_name', ''),
                        'Short Name': branding.get('short_name', ''),
                        'Title Template': branding.get('newsletter_title_template', ''),
                        'Footer Text': branding.get('footer_text', ''),
                        'Footer URL': branding.get('footer_url', ''),
                        'Footer URL Display': branding.get('footer_url_display', '')
                    })
            
            if branding_data:
                df_branding = pd.DataFrame(branding_data)
                df_branding.to_excel(writer, sheet_name='Branding', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    except Exception as e:
        st.error(f"Error exporting to Excel: {e}")
        return None

def export_customer_configs(customer_id: str) -> Optional[bytes]:
    """
    Export single customer configuration to Excel
    
    Args:
        customer_id: Customer identifier
    
    Returns:
        Excel file as bytes, or None if error
    """
    try:
        details = get_customer_details(customer_id)
        if not details:
            st.error(f"Customer {customer_id} not found")
            return None
        
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Customer Info
            info = details.get('info', {})
            df_info = pd.DataFrame([{
                'Customer ID': customer_id,
                'Company Name': info.get('company_name', ''),
                'Status': info.get('status', ''),
                'Contact Name': info.get('contact_name', ''),
                'Contact Email': info.get('contact_email', ''),
                'Phone': info.get('phone', ''),
                'Subscription Tier': info.get('subscription_tier', '')
            }])
            df_info.to_excel(writer, sheet_name='Customer Info', index=False)
            
            # Keywords
            keywords = details.get('keywords', {}).get('keywords', [])
            if keywords:
                df_keywords = pd.DataFrame([{'Keyword': k} for k in keywords])
                df_keywords.to_excel(writer, sheet_name='Keywords', index=False)
            
            # RSS Feeds
            feeds = details.get('feeds', {}).get('feeds', [])
            if feeds:
                df_feeds = pd.DataFrame([
                    {
                        'Feed Name': f.get('name', ''),
                        'Feed URL': f.get('url', ''),
                        'Enabled': f.get('enabled', True)
                    }
                    for f in feeds
                ])
                df_feeds.to_excel(writer, sheet_name='RSS Feeds', index=False)
            
            # Branding
            branding = details.get('branding', {})
            df_branding = pd.DataFrame([{
                'Application Name': branding.get('application_name', ''),
                'Short Name': branding.get('short_name', ''),
                'Title Template': branding.get('newsletter_title_template', ''),
                'Footer Text': branding.get('footer_text', ''),
                'Footer URL': branding.get('footer_url', ''),
                'Footer URL Display': branding.get('footer_url_display', '')
            }])
            df_branding.to_excel(writer, sheet_name='Branding', index=False)
        
        output.seek(0)
        return output.getvalue()
    
    except Exception as e:
        st.error(f"Error exporting customer config: {e}")
        return None

def import_configs_from_excel(file: io.BytesIO) -> Dict:
    """
    Import configurations from Excel file
    
    Args:
        file: Excel file as BytesIO or file upload
    
    Returns:
        Dictionary with success status and results
    """
    try:
        # Read all sheets
        excel_file = pd.ExcelFile(file)
        
        imported_count = 0
        errors = []
        
        # Read Customers sheet
        if 'Customers' in excel_file.sheet_names:
            df_customers = pd.read_excel(excel_file, sheet_name='Customers')
            
            for _, row in df_customers.iterrows():
                customer_id = str(row.get('Customer ID', '')).strip()
                if not customer_id or customer_id == 'nan':
                    continue
                
                try:
                    # Update customer info
                    info_updates = {
                        'company_name': str(row.get('Company Name', '')),
                        'status': str(row.get('Status', 'Active')),
                        'contact_name': str(row.get('Contact Name', '')),
                        'contact_email': str(row.get('Contact Email', '')),
                        'phone': str(row.get('Phone', '')),
                        'subscription_tier': str(row.get('Subscription Tier', 'Standard'))
                    }
                    
                    update_customer_info_admin(customer_id, info_updates)
                    imported_count += 1
                
                except Exception as e:
                    errors.append(f"Error updating customer {customer_id}: {str(e)}")
        
        # Read Keywords sheet
        if 'Keywords' in excel_file.sheet_names:
            df_keywords = pd.read_excel(excel_file, sheet_name='Keywords')
            
            # Group by customer
            keywords_by_customer = {}
            for _, row in df_keywords.iterrows():
                customer_id = str(row.get('Customer ID', '')).strip()
                keyword = str(row.get('Keyword', '')).strip()
                if customer_id and keyword and customer_id != 'nan' and keyword != 'nan':
                    if customer_id not in keywords_by_customer:
                        keywords_by_customer[customer_id] = []
                    keywords_by_customer[customer_id].append(keyword)
            
            # Update keywords for each customer
            for customer_id, keywords in keywords_by_customer.items():
                try:
                    keywords_data = {
                        'keywords': keywords,
                        'last_updated': 'admin',
                        'updated_at': datetime.now().isoformat()
                    }
                    update_customer_config(customer_id, "keywords", keywords_data, f"Admin: Import keywords from Excel")
                    imported_count += 1
                except Exception as e:
                    errors.append(f"Error updating keywords for {customer_id}: {str(e)}")
        
        # Read RSS Feeds sheet
        if 'RSS Feeds' in excel_file.sheet_names:
            df_feeds = pd.read_excel(excel_file, sheet_name='RSS Feeds')
            
            # Group by customer
            feeds_by_customer = {}
            for _, row in df_feeds.iterrows():
                customer_id = str(row.get('Customer ID', '')).strip()
                feed_name = str(row.get('Feed Name', '')).strip()
                feed_url = str(row.get('Feed URL', '')).strip()
                enabled = row.get('Enabled', True)
                
                if customer_id and feed_name and feed_url and customer_id != 'nan':
                    if customer_id not in feeds_by_customer:
                        feeds_by_customer[customer_id] = []
                    feeds_by_customer[customer_id].append({
                        'name': feed_name,
                        'url': feed_url,
                        'enabled': bool(enabled) if enabled not in ['nan', None] else True
                    })
            
            # Update feeds for each customer
            for customer_id, feeds in feeds_by_customer.items():
                try:
                    feeds_data = {
                        'feeds': feeds,
                        'last_updated': 'admin',
                        'updated_at': datetime.now().isoformat()
                    }
                    update_customer_config(customer_id, "feeds", feeds_data, f"Admin: Import feeds from Excel")
                    imported_count += 1
                except Exception as e:
                    errors.append(f"Error updating feeds for {customer_id}: {str(e)}")
        
        # Read Branding sheet
        if 'Branding' in excel_file.sheet_names:
            df_branding = pd.read_excel(excel_file, sheet_name='Branding')
            
            for _, row in df_branding.iterrows():
                customer_id = str(row.get('Customer ID', '')).strip()
                if not customer_id or customer_id == 'nan':
                    continue
                
                try:
                    branding_data = {
                        'application_name': str(row.get('Application Name', '')),
                        'short_name': str(row.get('Short Name', '')),
                        'newsletter_title_template': str(row.get('Title Template', '{name} - Week {week}')),
                        'footer_text': str(row.get('Footer Text', '')),
                        'footer_url': str(row.get('Footer URL', '')),
                        'footer_url_display': str(row.get('Footer URL Display', ''))
                    }
                    update_customer_config(customer_id, "branding", branding_data, f"Admin: Import branding from Excel")
                    imported_count += 1
                except Exception as e:
                    errors.append(f"Error updating branding for {customer_id}: {str(e)}")
        
        return {
            'success': True,
            'count': imported_count,
            'errors': errors
        }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'count': 0,
            'errors': []
        }

