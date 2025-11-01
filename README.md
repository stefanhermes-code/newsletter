# Newsletter Tool Cloud (GlobalNewsPilot)

Multi-tenant newsletter generation application built with Streamlit.

## Applications

- **GlobalNewsPilot** (`globalnewspilot`) - Multi-tenant User App for newsletter generation
- **GNP_Admin** (`GNP_Admin`) - Admin Dashboard for customer management and monitoring

## Repository Structure

- `admin_modules/` - Admin dashboard modules
- `user_modules/` - User app modules
- `streamlit_admin_app.py` - Admin dashboard entry point (GNP_Admin)
- `streamlit_user_app.py` - User application entry point (GlobalNewsPilot - multi-tenant)
- `customers/` - Customer-specific data and configurations

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Streamlit Secrets** (REQUIRED):
   - See [Streamlit Secrets Setup Guide](./STREAMLIT_SECRETS_SETUP.md)
   - Required secrets:
     - `github_token` - GitHub Personal Access Token (with `repo` permissions)
     - `github_repo` - Repository name (e.g., `"stefanhermes-code/newsletter"`)

3. Deploy to Streamlit Cloud:
   - **GNP_Admin**: Deploy `streamlit_admin_app.py`
   - **GlobalNewsPilot (gnpuser)**: Deploy `streamlit_user_app.py` (one-time, multi-tenant deployment)

## Documentation

- **Design Document:** `Newsletter Tool Cloud Migration - DESIGN DOCUMENT.md`
- **Implementation Plan:** `Newsletter Tool Cloud Migration - IMPLEMENTATION PLAN.md`
- **Onboarding Guide:** `ONBOARDING_PROCESS_GUIDE.md`
- **Setup Checklist:** `PRE-CODING_SETUP_CHECKLIST.md`

## Features

- Multi-tenant architecture (one GlobalNewsPilot app for all customers)
- Multi-user support with payment tier-based permissions
- Customer onboarding integrated in GNP_Admin
- Newsletter generation from Google News and RSS feeds
- Admin dashboard (GNP_Admin) for customer and configuration management

## Repository

GitHub: `stefanhermes-code/newsletter`

