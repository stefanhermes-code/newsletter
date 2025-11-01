"""
Onboarding Application

Customer-facing onboarding form for new newsletter setup.
"""

import streamlit as st
from urllib.parse import parse_qs

# Page configuration
st.set_page_config(
    page_title="Newsletter Tool - Onboarding",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state
if 'onboarding_token' not in st.session_state:
    st.session_state.onboarding_token = None

if 'onboarding_step' not in st.session_state:
    st.session_state.onboarding_step = 1

if 'onboarding_data' not in st.session_state:
    st.session_state.onboarding_data = {}

def get_token_from_url():
    """Get onboarding token from URL query parameters"""
    query_params = st.query_params
    token = query_params.get('token', [None])[0] if 'token' in query_params else None
    email = query_params.get('email', [None])[0] if 'email' in query_params else None
    return token, email

def validate_token(token):
    """Validate onboarding token - placeholder"""
    # TODO: Implement token validation with GitHub or database
    if token:
        return True
    return False

def save_progress(step, data):
    """Save onboarding progress - placeholder"""
    # TODO: Implement progress saving
    pass

def submit_onboarding(data):
    """Submit completed onboarding form - placeholder"""
    # TODO: Implement form submission
    st.success("Your information has been received! We'll review and set up your account shortly.")
    return True

def main():
    # Get token from URL
    token, email = get_token_from_url()
    
    if not token:
        st.title("Invalid Onboarding Link")
        st.error("No valid onboarding token found. Please use the link provided in your email.")
        st.info("If you received an onboarding email, make sure you're using the complete link.")
        return
    
    # Validate token
    if not validate_token(token):
        st.title("Invalid Onboarding Link")
        st.error("This onboarding link is invalid or has expired.")
        st.info("Please contact support for a new onboarding link.")
        return
    
    st.session_state.onboarding_token = token
    
    # Show progress indicator
    steps = [
        "Company Information",
        "Newsletter Branding",
        "News Topics",
        "News Sources",
        "Contact Information",
        "Review",
        "Submit"
    ]
    
    progress = st.session_state.onboarding_step / len(steps)
    st.progress(progress)
    st.caption(f"Step {st.session_state.onboarding_step} of {len(steps)}: {steps[st.session_state.onboarding_step - 1]}")
    
    st.title("Set Up Your Newsletter Tool")
    st.markdown("---")
    
    # Multi-step form
    with st.form(f"onboarding_step_{st.session_state.onboarding_step}"):
        if st.session_state.onboarding_step == 1:
            render_step1_company_info()
        elif st.session_state.onboarding_step == 2:
            render_step2_branding()
        elif st.session_state.onboarding_step == 3:
            render_step3_keywords()
        elif st.session_state.onboarding_step == 4:
            render_step4_feeds()
        elif st.session_state.onboarding_step == 5:
            render_step5_contact(email)
        elif st.session_state.onboarding_step == 6:
            render_step6_review()
        elif st.session_state.onboarding_step == 7:
            render_step7_submit()
        
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.session_state.onboarding_step > 1:
                if st.form_submit_button("← Back"):
                    st.session_state.onboarding_step -= 1
                    st.rerun()
        
        with col3:
            if st.session_state.onboarding_step < len(steps):
                if st.form_submit_button("Next →", type="primary"):
                    # Save progress
                    save_progress(st.session_state.onboarding_step, st.session_state.onboarding_data)
                    st.session_state.onboarding_step += 1
                    st.rerun()
            else:
                if st.form_submit_button("Submit", type="primary"):
                    if submit_onboarding(st.session_state.onboarding_data):
                        st.session_state.onboarding_step = 8  # Show success page

def render_step1_company_info():
    """Step 1: Company Information"""
    st.header("Company Information")
    
    company_name = st.text_input("Company Name *", value=st.session_state.onboarding_data.get('company_name', ''))
    short_name = st.text_input("Short Name (for file naming) *", 
                              value=st.session_state.onboarding_data.get('short_name', ''),
                              help="Short name will be used in file names")
    
    st.session_state.onboarding_data['company_name'] = company_name
    st.session_state.onboarding_data['short_name'] = short_name

def render_step2_branding():
    """Step 2: Newsletter Branding"""
    st.header("Newsletter Branding")
    
    application_name = st.text_input(
        "What should your newsletter be called? *",
        value=st.session_state.onboarding_data.get('application_name', ''),
        help="Example: 'ACME Industry Newsletter'"
    )
    
    footer_text = st.text_input(
        "Footer Text *",
        value=st.session_state.onboarding_data.get('footer_text', ''),
        help="This appears at the bottom of each newsletter"
    )
    
    footer_url = st.text_input(
        "Your Website URL *",
        value=st.session_state.onboarding_data.get('footer_url', ''),
        help="Example: https://www.yourcompany.com"
    )
    
    st.session_state.onboarding_data['application_name'] = application_name
    st.session_state.onboarding_data['footer_text'] = footer_text
    st.session_state.onboarding_data['footer_url'] = footer_url

def render_step3_keywords():
    """Step 3: News Topics (Optional)"""
    st.header("News Topics (Optional)")
    st.info("You can add more keywords later in the app. This step is optional.")
    
    if st.checkbox("Skip this step for now"):
        st.session_state.onboarding_data['keywords'] = []
        return
    
    # Placeholder for keyword input - will be enhanced
    st.write("Keyword input interface coming soon")
    st.session_state.onboarding_data['keywords'] = []

def render_step4_feeds():
    """Step 4: News Sources (Optional)"""
    st.header("News Sources (Optional)")
    st.info("You can add RSS feeds later in the app. This step is optional.")
    
    if st.checkbox("Skip this step for now"):
        st.session_state.onboarding_data['feeds'] = []
        return
    
    # Placeholder for feed input - will be enhanced
    st.write("RSS feed input interface coming soon")
    st.session_state.onboarding_data['feeds'] = []

def render_step5_contact(email):
    """Step 5: Contact Information"""
    st.header("Contact Information")
    
    your_name = st.text_input("Your Name *", value=st.session_state.onboarding_data.get('contact_name', ''))
    phone = st.text_input("Phone Number", value=st.session_state.onboarding_data.get('phone', ''))
    
    # Email is pre-filled from URL
    st.text_input("Email", value=email, disabled=True)
    
    st.session_state.onboarding_data['contact_name'] = your_name
    st.session_state.onboarding_data['phone'] = phone
    st.session_state.onboarding_data['email'] = email

def render_step6_review():
    """Step 6: Review"""
    st.header("Review Your Information")
    
    st.subheader("Company Information")
    st.write(f"**Company Name:** {st.session_state.onboarding_data.get('company_name', 'N/A')}")
    st.write(f"**Short Name:** {st.session_state.onboarding_data.get('short_name', 'N/A')}")
    
    st.subheader("Branding")
    st.write(f"**Newsletter Name:** {st.session_state.onboarding_data.get('application_name', 'N/A')}")
    st.write(f"**Footer Text:** {st.session_state.onboarding_data.get('footer_text', 'N/A')}")
    st.write(f"**Website URL:** {st.session_state.onboarding_data.get('footer_url', 'N/A')}")
    
    st.subheader("Contact Information")
    st.write(f"**Name:** {st.session_state.onboarding_data.get('contact_name', 'N/A')}")
    st.write(f"**Email:** {st.session_state.onboarding_data.get('email', 'N/A')}")
    st.write(f"**Phone:** {st.session_state.onboarding_data.get('phone', 'N/A')}")
    
    st.info("Please review your information. You can go back to edit if needed.")

def render_step7_submit():
    """Step 7: Submit"""
    st.header("Submit")
    st.success("Ready to submit!")
    st.write("Click the Submit button below to send your information.")

if __name__ == "__main__":
    main()

