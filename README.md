# Newsletter Tool Cloud

Multi-tenant newsletter generation application built with Streamlit.

## Repository Structure

- `admin_modules/` - Admin dashboard modules
- `user_modules/` - User app modules
- `onboarding_app/` - Customer onboarding application
- `streamlit_admin_app.py` - Admin dashboard entry point
- `streamlit_user_app.py` - User application entry point (multi-tenant)
- `streamlit_onboarding_app.py` - Onboarding application entry point
- `customers/` - Customer-specific data and configurations

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure Streamlit secrets (see Design Document)

3. Deploy to Streamlit Cloud:
   - Admin App: Deploy `streamlit_admin_app.py`
   - User App: Deploy `streamlit_user_app.py` (one-time, multi-tenant)
   - Onboarding App: Deploy `streamlit_onboarding_app.py`

## Documentation

- **Design Document:** `Newsletter Tool Cloud Migration - DESIGN DOCUMENT.md`
- **Implementation Plan:** `Newsletter Tool Cloud Migration - IMPLEMENTATION PLAN.md`
- **Onboarding Guide:** `ONBOARDING_PROCESS_GUIDE.md`
- **Setup Checklist:** `PRE-CODING_SETUP_CHECKLIST.md`

## Features

- Multi-tenant architecture (one User App for all customers)
- Multi-user support with payment tier-based permissions
- Customer onboarding via web form
- Newsletter generation from Google News and RSS feeds
- Admin dashboard for customer and configuration management

## Repository

GitHub: `stefanhermes-code/newsletter`

