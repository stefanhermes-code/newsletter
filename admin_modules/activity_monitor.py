"""
Activity Monitor Module

Monitor customer activities including newsletter generation and article finding.
"""

import streamlit as st
from typing import List, Dict, Optional
from admin_modules.github_admin import (
    list_customer_files,
    get_file_content,
    list_all_customers
)
from admin_modules.customer_manager import get_customer_details
from datetime import datetime

def render_activity_monitoring():
    """Render activity monitoring interface"""
    st.header("Activity Monitoring")
    
    # Customer selector
    all_customer_ids = ["-- All Customers --"] + list_all_customers()
    selected_customer = st.selectbox(
        "Select Customer",
        all_customer_ids,
        key="activity_customer_selector"
    )
    
    if selected_customer == "-- All Customers --":
        render_all_customers_activity()
    else:
        render_customer_activity(selected_customer)

def render_customer_activity(customer_id: str):
    """Render activity for a specific customer"""
    st.subheader(f"Activity for: {customer_id}")
    
    tab1, tab2 = st.tabs(["Newsletters", "Configuration Changes"])
    
    with tab1:
        render_newsletter_activity(customer_id)
    
    with tab2:
        render_config_activity(customer_id)

def render_newsletter_activity(customer_id: str):
    """Show newsletter generation activity"""
    st.subheader("Newsletter Activity")
    
    # List newsletters
    newsletter_files = list_customer_files(customer_id, "data/newsletters")
    
    if newsletter_files:
        # Filter HTML files
        newsletters = [f for f in newsletter_files if f.get('name', '').endswith('.html')]
        
        st.write(f"**{len(newsletters)} newsletter(s) generated**")
        
        # Sort by last_modified (newest first)
        newsletters.sort(key=lambda x: x.get('last_modified', ''), reverse=True)
        
        for newsletter in newsletters:
            with st.expander(f"**{newsletter.get('name')}**"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Size:** {newsletter.get('size', 0)} bytes")
                    st.write(f"**Modified:** {newsletter.get('last_modified', 'Unknown')}")
                
                with col2:
                    # View button
                    if st.button("👁️ View", key=f"view_nl_{newsletter.get('name')}"):
                        content = get_file_content(customer_id, f"data/newsletters/{newsletter.get('name')}")
                        if content:
                            st.markdown("### Newsletter Preview")
                            st.components.v1.html(content, height=600, scrolling=True)
                
                with col3:
                    # Download button
                    if content := get_file_content(customer_id, f"data/newsletters/{newsletter.get('name')}"):
                        st.download_button(
                            label="📥 Download",
                            data=content,
                            file_name=newsletter.get('name'),
                            mime="text/html",
                            key=f"download_nl_{newsletter.get('name')}"
                        )
        
        # Stats
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if newsletters:
                latest = newsletters[0].get('last_modified', '')
                st.metric("Latest Newsletter", latest[:10] if latest else "N/A")
        with col2:
            st.metric("Total Newsletters", len(newsletters))
    else:
        st.info("No newsletters generated yet for this customer.")

def render_config_activity(customer_id: str):
    """Show configuration change activity"""
    st.subheader("Configuration Change Activity")
    
    from admin_modules.github_admin import get_commit_history
    
    config_files = ["keywords.json", "feeds.json", "branding.json", "user_access.json"]
    
    all_changes = []
    for config_file in config_files:
        history = get_commit_history(customer_id, f"config/{config_file}" if config_file != "user_access.json" else "", limit=10)
        for commit in history:
            commit['config_file'] = config_file
            all_changes.append(commit)
    
    # Sort by date (newest first)
    all_changes.sort(key=lambda x: x.get('date', ''), reverse=True)
    
    if all_changes:
        st.write(f"**{len(all_changes)} recent configuration changes**")
        
        for change in all_changes[:30]:  # Show last 30 changes
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                st.write(f"**{change.get('config_file')}**")
                st.caption(change.get('date', 'Unknown')[:19] if change.get('date') else 'Unknown')
            
            with col2:
                st.write(change.get('message', 'No message')[:80])
            
            with col3:
                st.write(f"By: {change.get('author', 'Unknown')}")
                if change.get('url'):
                    st.markdown(f"[View]({change['url']})")
            
            st.markdown("---")
    else:
        st.info("No configuration changes recorded yet.")

def render_all_customers_activity():
    """Show activity across all customers"""
    st.subheader("All Customers Activity Summary")
    
    all_customers = list_all_customers()
    
    if not all_customers:
        st.info("No customers found.")
        return
    
    # Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    total_newsletters = 0
    customers_with_newsletters = 0
    
    for customer_id in all_customers:
        newsletters = list_customer_files(customer_id, "data/newsletters")
        newsletter_count = len([f for f in newsletters if f.get('name', '').endswith('.html')])
        if newsletter_count > 0:
            total_newsletters += newsletter_count
            customers_with_newsletters += 1
    
    with col1:
        st.metric("Total Customers", len(all_customers))
    with col2:
        st.metric("Active Customers", customers_with_newsletters)
    with col3:
        st.metric("Total Newsletters", total_newsletters)
    with col4:
        st.metric("Avg per Customer", round(total_newsletters / len(all_customers), 1) if all_customers else 0)
    
    st.markdown("---")
    
    # Customer activity list
    st.subheader("Customer Activity")
    
    for customer_id in all_customers:
        customer_details = get_customer_details(customer_id)
        if not customer_details:
            continue
        
        company_name = customer_details.get('info', {}).get('company_name', customer_id)
        newsletters = list_customer_files(customer_id, "data/newsletters")
        newsletter_count = len([f for f in newsletters if f.get('name', '').endswith('.html')])
        
        with st.expander(f"**{company_name}** ({customer_id}) - {newsletter_count} newsletter(s)"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                keywords_count = len(customer_details.get('keywords', {}).get('keywords', []))
                st.metric("Keywords", keywords_count)
            
            with col2:
                feeds_count = len(customer_details.get('feeds', {}).get('feeds', []))
                st.metric("RSS Feeds", feeds_count)
            
            with col3:
                users_count = len(customer_details.get('user_access', {}).get('users', []))
                st.metric("Users", users_count)
            
            if st.button(f"View Details", key=f"view_activity_{customer_id}"):
                st.session_state.activity_customer_selector = customer_id
                st.rerun()

