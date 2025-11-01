# Pre-Coding Setup Checklist

**Repository:** `stefanhermes-code/newsletter`

This checklist outlines everything you need to set up before starting development.

---

## ✅ Phase 1: GitHub Repository Setup

### 1.1 Repository Folder Structure (Not Branches!)

**Important:** This is about creating **folders/directories** in your repository, NOT Git branches. You'll use one main branch (usually `main` or `master`).

- [ ] Create these **folders** in `stefanhermes-code/newsletter` repository:
  ```
  admin_modules/          # Folder for admin dashboard Python modules
  user_modules/          # Folder for user app Python modules
  onboarding_app/        # Folder for onboarding application
  config/                # Folder for shared configuration files
  customers/             # Folder where customer data will be stored
  ```
  
  **How to create:**
  - Via GitHub web interface: Click "Add file" → "Create new file" → Type `admin_modules/.gitkeep` → Commit
  - Via Git commands: `mkdir admin_modules user_modules onboarding_app config customers`
  - Or just create empty Python files in each: `admin_modules/__init__.py`, etc.

- [ ] Create main app files in repository **root** (not in folders):
  - `streamlit_admin_app.py` - Main entry point for admin dashboard
  - `streamlit_user_app.py` - Main entry point for user app
  - `streamlit_onboarding_app.py` - Main entry point for onboarding app
- [ ] Create `requirements.txt` (see Section 2 below)
- [ ] Create `.gitignore` file
- [ ] Create `README.md` (basic structure)

### 1.2 GitHub Access
- [ ] Generate GitHub Personal Access Token (PAT) with `repo` scope
  - Go to: https://github.com/settings/tokens
  - Generate new token (classic)
  - Name: "Newsletter Tool Admin"
  - Scopes: `repo` (full control)
  - Copy token immediately (you won't see it again!)
  - **Save token securely** - you'll need it for Streamlit secrets

---

## ✅ Phase 2: Python Dependencies

### 2.1 Create `requirements.txt`

Create this file in your repository root:

```txt
# Streamlit Framework
streamlit>=1.28.0

# GitHub API
PyGithub>=2.1.1

# Data Manipulation
pandas>=2.0.0
openpyxl>=3.1.0

# Date/Time
python-dateutil>=2.8.2

# Email Sending (choose one or multiple)
# Option A: SMTP (built-in, but include for email libraries)
# No extra package needed for smtplib

# Option B: Third-party email services (uncomment as needed)
# sendgrid>=6.10.0
# mailgun>=2.0.0
# boto3>=1.28.0  # For AWS SES

# News/Web Scraping (for Google News and RSS)
requests>=2.31.0
feedparser>=6.0.10
beautifulsoup4>=4.12.0
lxml>=4.9.0

# HTML Processing
html2text>=2020.1.16

# Utilities
python-dotenv>=1.0.0
```

**Action:** Create this file and commit to repository.

---

## ✅ Phase 3: Repository Files Setup

### 3.1 `.gitignore` File

Create `.gitignore` in repository root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv
*.egg-info/
dist/
build/

# Streamlit
.streamlit/secrets.toml
.streamlit/config.toml

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
*.xlsx
!customers/*/data/*.xlsx  # Keep customer database files
.env
.env.local

# Temporary files
*.tmp
*.bak
```

**Action:** Create this file and commit to repository.

### 3.2 Basic `README.md`

Create a basic README (you can expand later):

```markdown
# Newsletter Tool Cloud

Multi-tenant newsletter generation application built with Streamlit.

## Repository Structure

- `admin_modules/` - Admin dashboard modules
- `user_modules/` - User app modules
- `onboarding_app/` - Customer onboarding application
- `streamlit_admin_app.py` - Admin dashboard entry point
- `streamlit_user_app.py` - User application entry point
- `streamlit_onboarding_app.py` - Onboarding application entry point
- `customers/` - Customer-specific data and configurations

## Setup

See Design Document and Implementation Plan for detailed setup instructions.

## Deployment

- Admin App: Deploy `streamlit_admin_app.py` to Streamlit Cloud
- User App: Deploy `streamlit_user_app.py` to Streamlit Cloud (one-time, multi-tenant)
- Onboarding App: Deploy `streamlit_onboarding_app.py` to Streamlit Cloud
```

**Action:** Create this file and commit to repository.

---

## ✅ Phase 4: Streamlit Cloud Setup (Preparation)

### 4.1 Streamlit Cloud Account
- [ ] Sign up/login to Streamlit Cloud: https://share.streamlit.io
- [ ] Connect your GitHub account (`stefanhermes-code/newsletter`)
- [ ] Verify repository is accessible

### 4.2 Prepare Streamlit Secrets (for later)

**Note:** You'll configure these when deploying apps, but prepare the values now.

#### Admin App Secrets (to be added when deploying):
```toml
# Streamlit Cloud → Admin App → Settings → Secrets
github_repo = "stefanhermes-code/newsletter"
github_token = "ghp_..."  # Your GitHub PAT
admin_email = "your-admin-email@domain.com"

[email]
# Choose one option below:

# Option A: SMTP
smtp_server = "smtp.gmail.com"  # or your SMTP server
smtp_port = 587
smtp_username = "your-email@gmail.com"
smtp_password = "your-app-password"
from_email = "noreply@yourcompany.com"
from_name = "Newsletter Tool"

# Option B: SendGrid (uncomment if using)
# service = "sendgrid"
# api_key = "SG.xxxxxxxxxxxxx"
# from_email = "noreply@yourcompany.com"
# from_name = "Newsletter Tool"
```

#### User App Secrets (to be added when deploying):
```toml
# Streamlit Cloud → User App → Settings → Secrets
github_repo = "stefanhermes-code/newsletter"
github_token = "ghp_..."  # Your GitHub PAT (can be same as admin)
admin_email = "your-admin-email@domain.com"
```

#### Onboarding App Secrets (to be added when deploying):
```toml
# Streamlit Cloud → Onboarding App → Settings → Secrets
github_repo = "stefanhermes-code/newsletter"
github_token = "ghp_..."  # Your GitHub PAT
admin_email = "your-admin-email@domain.com"
```

**Action:** Keep these templates ready - you'll add them in Streamlit Cloud UI during deployment.

---

## ✅ Phase 5: Email Configuration (If Using Email Sending)

### 5.1 Choose Email Service

**Option A: SMTP (Gmail/Outlook)**
- [ ] Get SMTP credentials:
  - **Gmail:** Enable "App Password" in Google Account settings
  - **Outlook:** Use app password or OAuth
- [ ] Document SMTP settings (server, port, username, password)

**Option B: Third-Party Service**
- [ ] Sign up for service (SendGrid, Mailgun, AWS SES)
- [ ] Get API key
- [ ] Document API credentials

**Action:** Have email credentials ready before deploying apps.

**Note:** If you skip email setup initially, you can use the manual admin entry method for onboarding.

---

## ✅ Phase 6: Initial Repository Commit

### 6.1 Basic File Structure
- [ ] Initialize Git in repository (if not already done)
- [ ] Commit folder structure by creating `__init__.py` files in each folder:
  ```
  admin_modules/__init__.py
  user_modules/__init__.py
  onboarding_app/__init__.py
  config/__init__.py
  customers/.gitkeep  # (or README.md explaining this folder)
  ```
  
  **Note:** In Git, empty folders aren't tracked. To commit a folder structure, create a file in each folder:
  - For Python packages: Create `__init__.py` (makes it a Python package)
  - For empty folders: Create `.gitkeep` or a `README.md` file
- [ ] Commit `requirements.txt`
- [ ] Commit `.gitignore`
- [ ] Commit `README.md`

**Action:** Make initial commit to establish repository structure.

---

## ✅ Phase 7: Development Environment

### 7.1 Local Setup (Optional but Recommended)
- [ ] Install Python 3.9+ (if not already installed)
- [ ] Create virtual environment:
  ```bash
  python -m venv venv
  ```
- [ ] Activate virtual environment:
  ```bash
  # Windows
  venv\Scripts\activate
  
  # Mac/Linux
  source venv/bin/activate
  ```
- [ ] Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

**Action:** Set up local environment if you want to test before deploying.

---

## ✅ Phase 8: Test GitHub Connection

### 8.1 Verify Repository Access
- [ ] Test GitHub token works:
  - Can access `stefanhermes-code/newsletter`
  - Can read repository
  - Can write/commit (test with a dummy file)

**Action:** Verify GitHub token has correct permissions before coding.

---

## 📋 Summary Checklist

Before starting to code, ensure you have:

- [x] GitHub repository: `stefanhermes-code/newsletter` ✅ (you already have this)
- [ ] Repository folder structure created
- [ ] `requirements.txt` created and committed
- [ ] `.gitignore` created and committed
- [ ] `README.md` created and committed
- [ ] GitHub Personal Access Token generated and saved securely
- [ ] Streamlit Cloud account set up
- [ ] Email service configured (or decided to skip for now)
- [ ] GitHub token tested (can read/write to repository)

---

## 🚀 Ready to Code?

Once all items above are checked, you're ready to:
1. Start implementing `github_admin.py` (core GitHub operations)
2. Create basic app skeletons (`streamlit_admin_app.py`, `streamlit_user_app.py`)
3. Implement `customer_manager.py` (basic CRUD)

---

## Next Steps After Setup

1. **Phase 1: Foundation**
   - Implement `github_admin.py` - connect to `stefanhermes-code/newsletter`
   - Implement `customer_manager.py` - basic customer CRUD
   - Create admin app skeleton

2. **Phase 2: Onboarding**
   - Implement onboarding wizard
   - Test config file creation in GitHub

3. **Phase 3: User App**
   - Implement customer selector
   - Implement news finding
   - Implement newsletter generation

4. **Phase 4: Deployment**
   - Deploy apps to Streamlit Cloud
   - Configure secrets
   - Test end-to-end

---

## Questions?

- If email setup is blocking you → Skip it, use manual admin entry for now
- If Streamlit Cloud not ready → Develop locally first, deploy later
- If GitHub token issues → Test token permissions first

**Most Important:** Repository structure and `requirements.txt` - get these done first!

---

**Document Created:** 2025-01-XX
**Repository:** `stefanhermes-code/newsletter`

