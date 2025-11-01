# Newsletter Tool Cloud Migration - Design Document

## Executive Summary

This document outlines the design for migrating the Newsletter Tool (currently Flask-based desktop applications) to Streamlit Cloud applications. The system supports multiple customer deployments (e.g., HTC, APBA) from a single codebase with customer-specific configurations.

**Current State:** Two separate Flask applications (HTC Newsletter Tool, APBA NewsBulletin) with hardcoded customer-specific elements.

**Target State:** Single Streamlit application deployable per customer with all customer-specific elements externalized to configuration.

---

## Architecture Overview

### Two-Application System (Same GitHub Repository)

#### **Application 1: User App (`streamlit_user_app.py`)**
- **Purpose:** Multi-tenant application where users find news articles (via Google search and RSS feeds) and generate newsletters from selected articles for different customers/brands (e.g., HTC, APBA)
- **Multi-Tenant Architecture:**
  - Single User App deployment (e.g., `newsletter-user.streamlit.app`)
  - Users can access multiple newsletters (customers) tied to their email address
  - Customer selector at app start/login to switch between newsletters
  - Each newsletter has separate branding, config, and data
  - Users can switch between their accessible newsletters at any time
- **Core Functionality (Primary Features):**
  - **News Finding:**
    - Find news articles using Google search (primary method)
    - Find news articles from configured RSS feeds
    - Configure search time period (last 7 days, 14 days, 30 days, etc.)
    - Background processing - users don't see technical details
    - Simple status indicator (e.g., "Finding news..." or "Ready")
  - **Article Dashboard:**
    - View found articles with title, date, source, category
    - **Article Preview:** Users can preview article content before selecting
    - Filter articles by category
    - Search articles by keywords
    - View articles from configurable date range
    - Article selection interface (checkboxes or selection buttons)
  - **Newsletter Generation:**
    - Select articles for newsletter (with preview capability)
    - Generate newsletter directly from selected articles
    - Output: Formatted HTML newsletter ready for use
    - Mark selected articles as "used" (prevents duplicate selection)
    - Download/view formatted newsletters
    - No intermediate draft step - direct newsletter generation
  - **Configuration Management Tab:**
    - Users can edit keywords and RSS feeds at any time
    - Simple forms for adding/editing/deleting keywords and feeds
    - Real-time validation before saving
    - **Background Save:** Changes saved automatically to GitHub (invisible to user)
    - No technical terms visible - users just see "Save" or automatic saving
- **Customer/Newsletter Switching:**
  - **Newsletter selector always visible** in sidebar or header (not just at startup)
  - Dropdown or list shows all newsletters user has access to
  - Switch between newsletters at any time during app usage (e.g., HTC, APBA)
  - Each newsletter maintains its own state (selected articles, config, data)
  - Current newsletter context displayed in header/branding
  - User's permissions for selected newsletter determine which features are available (based on payment tier)
- **Deployment:** Single multi-tenant Streamlit Cloud instance (e.g., `newsletter-user.streamlit.app`)
  - One deployment serves all users
  - Users access their newsletters via customer selector
  - Config loaded dynamically based on selected customer

#### **Application 2: Admin Dashboard (`streamlit_admin_app.py`)**
- **Purpose:** Admin has complete visibility, control, and management of all customer deployments
- **Core Features:**
  - **Customer Management:**
    - Customer list with details (status, subscription, contact info)
    - Add new customers (onboarding wizard)
    - Edit customer information
    - Activate/deactivate customers
    - Delete/archive customers
    - Customer subscription management
  - **Customer Initialization & Setup:**
    - Multi-step onboarding wizard
    - Automated configuration file creation
    - Streamlit Cloud deployment setup
    - Access credentials provisioning
    - Post-deployment verification
  - **Full Visibility:**
    - View all customer configurations (keywords, feeds, branding)
    - Monitor customer activity (newsletters created, articles found, config changes)
    - See customer-generated content (newsletters, drafts, database entries)
    - Track configuration changes over time (history of edits to keywords/feeds)
  - **Configuration Management:**
    - View/edit any customer's config repository
    - Export JSON → Excel for advanced analysis
    - Import Excel → JSON for bulk updates
    - Compare configurations across customers
  - **Analytics & Insights:**
    - Cross-customer usage patterns
    - Popular keywords/feeds across customers
    - Customer engagement metrics
    - Trend analysis
    - Revenue/subscription analytics
- **Deployment:** Single admin Streamlit Cloud instance (e.g., `newsletter-admin.streamlit.app`)

---

## Customer Onboarding & Configuration Process

### Overview

When a new customer subscribes, we need to collect their specific requirements and configure the application accordingly. This section outlines the onboarding workflow and required customer information.

---

### Step 1: Customer Requirements Collection

**Recommended Approach: Customer Onboarding Webpage (Admin-Initiated)**

The most streamlined approach uses a separate onboarding webpage that customers fill out, initiated from the Admin Dashboard.

#### **Onboarding Workflow (Customer Webpage Method):**

**1. Admin Initiates Onboarding:**
   - Admin goes to Admin Dashboard → "Customer Management" → "Start Onboarding"
   - Enters customer email address
   - Optionally enters customer name (for personalized email)
   - Clicks "Send Onboarding Link"
   - System generates unique onboarding token and sends email to customer

**2. Customer Receives Email:**
   - Email contains personalized onboarding link
   - Link format: `onboarding.streamlit.app/start?token={unique_token}&email={customer_email}`
   - Link is time-limited (valid for 7 days)
   - Customer clicks link to open onboarding webpage

**3. Customer Completes Onboarding Form:**
   - Opens separate Streamlit onboarding app
   - Step-by-step form (same 7 steps, but customer-friendly language)
   - Can save progress and return later
   - Submits completed form
   - Submission appears in Admin Dashboard as "Pending Review"

**4. Admin Reviews & Approves:**
   - Admin sees submission in "Pending Onboarding" section
   - Admin reviews all information
   - Admin can edit if needed
   - Admin clicks "Create Customer Account" to approve
   - System automatically creates all configuration files

**5. System Actions (After Admin Approval):**
   - Validates customer ID (auto-generated or admin-set)
   - Creates GitHub folder structure
   - Generates `branding.json` from form data
   - Creates `keywords.json` (empty or with initial data)
   - Creates `feeds.json` (empty or with initial data)
   - Creates `customer_info.json` (contact/subscription info)
   - Creates `user_access.json` with empty users list: `{"users": []}` (ready for multi-user access)
   - Commits all files to GitHub
   - **Note:** No separate Streamlit secrets needed - User App is multi-tenant
   - Status: "Ready for User Access Assignment"

#### **Alternative: Manual Admin Entry (Fallback Method)**

If email sending is not configured or customer prefers, admin can manually enter information:

1. **Admin clicks "Add New Customer"** in Admin Dashboard
2. **Multi-Step Wizard Collects Information:**
   - Same 7 steps as customer form, but admin fills out
3. **System Actions:** (Same as Step 5 above)

**Best Practice Recommendation:**
- **Customer Onboarding Webpage:** Primary method - professional, streamlined, reduces admin workload
- **Manual Admin Entry:** Fallback option if email sending unavailable or customer prefers

---

### **Email Sending Requirements**

**⚠️ Critical Requirement:** The Customer Onboarding Webpage method requires email sending capability.

**Implementation Options:**

1. **SMTP (Simple Mail Transfer Protocol)**
   - Use `smtplib` (built-in Python library)
   - Configure SMTP server in Streamlit Secrets
   - Works with Gmail, Outlook, custom SMTP servers
   - Free but may have sending limits

2. **Third-Party Email Services**
   - SendGrid (free tier: 100/day)
   - Mailgun (free tier: 5,000/month)
   - AWS SES (very cheap, ~$0.10 per 1,000 emails)
   - Better deliverability and analytics

3. **Fallback Strategy:**
   - If email sending fails, display onboarding link in Admin Dashboard
   - Admin can manually copy and send link via their own email
   - System tracks invitation status regardless of delivery method

**Email Configuration:**
- Store email credentials in Streamlit Secrets (never hardcode)
- Required emails: onboarding invitation, welcome email, admin notifications
- Email templates should be customizable per customer

**Testing:**
- Test email sending before production deployment
- Verify emails don't go to spam
- Test fallback procedures if email fails

---

### Step 2: Required Customer Information

**Note:** All information collected during onboarding is stored in:
- `customers/{customer_id}/config/branding.json` (branding info)
- `customers/{customer_id}/config/keywords.json` (keywords)
- `customers/{customer_id}/config/feeds.json` (feeds)
- `customers/{customer_id}/customer_info.json` (contact/subscription info - admin-only)

#### **A. Branding & Identity (Required)**
These values will appear throughout the application and generated newsletters:

| Field | Example | Purpose |
|-------|---------|---------|
| Company Name | "ACME Corporation" | Full company name for branding |
| Short Name | "ACME" | Used in filenames, short references |
| Application Name | "ACME Industry Newsletter" | Main dashboard header |
| Newsletter Title Template | "{name} - Week {week}" | Format for newsletter titles |
| Footer Text | "Brought to you by ACME Corporation" | Newsletter footer text |
| Footer URL | "https://www.acme.com" | Company website URL |
| Footer URL Display | "www.acme.com" | Display text for footer link |

#### **B. Initial Configuration (Required)**
| Field | Example | Purpose |
|-------|---------|---------|
| Initial Keywords | `["polyurethane", "foam", "sustainability"]` | Search terms for Google News |
| Keyword Categories | `{"polyurethane": "Materials", "foam": "Materials"}` | Category mapping |
| RSS Feed URLs | `["https://example.com/rss", "..."]` | Initial news sources |
| Feed Categories | `{"https://example.com/rss": "Industry News"}` | Category assignments |

#### **C. File Naming Preferences (Optional - defaults provided)**
| Field | Default | Purpose |
|-------|---------|---------|
| Newsletter Filename Template | `"{short_name}_Newsletter_{timestamp}.html"` | Output newsletter naming |
| Database Filename | `"{customer_id}_News_Database.xlsx"` | Database file naming (internal use, not visible to users) |

#### **D. Contact & Subscription Information (Admin)**
| Field | Example | Purpose |
|-------|---------|---------|
| Contact Name | "John Doe" | Primary contact person |
| Contact Email | "john@acme.com" | Contact email address |
| Contact Phone | "+1-555-1234" | Contact phone number |
| Subscription Tier | "Standard" | Subscription plan level |
| Subscription Status | "Active" | Active/Inactive/Suspended |
| Start Date | "2025-01-15" | Subscription start date |
| Renewal Date | "2026-01-15" | Subscription renewal date |

#### **E. Technical Configuration (Admin)**
| Field | Example | Purpose |
|-------|---------|---------|
| Customer ID | `"acme"` (lowercase, alphanumeric) | Unique identifier |
| Streamlit App URL | `"acme-newsletter.streamlit.app"` | Deployment URL |
| GitHub Folder Path | `"customers/acme"` | Repository location |
| Deployment Date | "2025-01-15" | When app was deployed |
| GitHub Token | (generated/instructions) | Customer's GitHub token for access |

---

### Step 3: Configuration Storage & Automation

Once customer requirements are collected, the system automatically creates configuration files in GitHub.

#### **Automated Configuration Creation:**

The Admin Dashboard's onboarding wizard should:

1. **Validate Input:**
   - Check customer ID uniqueness
   - Validate URLs (footer, feeds)
   - Ensure required fields are filled

2. **Generate Configuration Files:**
   - Create `branding.json` with all branding information
   - Create `keywords.json` (empty or with initial keywords from form)
   - Create `feeds.json` (empty or with initial feeds from form)
   - Create `customer_info.json` with contact and subscription information (admin-only)
   - Create customer folder structure in GitHub

3. **Create Customer Record:**
   - Add customer to admin customer list/database
   - Set initial status to "Pending Deployment"
   - Store contact and subscription information
   - Record creation timestamp

4. **Commit to GitHub:**
   - Use GitHub API to create files in correct location
   - Commit with message: `"Initial configuration for customer: {customer_id}"`
   - Create branch if needed for review process

5. **Generate Deployment Assets:**
   - Output Streamlit secrets template
   - Generate customer deployment checklist
   - Create customer-specific README with access instructions

#### **GitHub Structure Created:**
```
github.com/{org}/{newsletter-tool-repo}/
└── customers/
    └── {customer_id}/
        ├── config/
        │   ├── branding.json       # Auto-generated from form
        │   ├── keywords.json      # Auto-generated (empty or with data)
        │   └── feeds.json         # Auto-generated (empty or with data)
        ├── customer_info.json      # Admin-only: contact, subscription info
        ├── user_access.json        # Multi-user access list with payment tiers
        └── data/
            ├── database.xlsx      # Created on first app run
            └── newsletters/       # Created on first newsletter generation
```

**User Access File Structure (`user_access.json`):**
- Stores multiple users with their payment tiers and permissions
- Format:
  ```json
  {
    "users": [
      {
        "email": "user1@email.com",
        "tier": "premium",
        "role": "admin",
        "permissions": ["view", "edit", "generate", "manage_config"],
        "added_date": "2025-01-15",
        "added_by": "admin@company.com"
      },
      {
        "email": "user2@email.com",
        "tier": "standard",
        "role": "editor",
        "permissions": ["view", "generate"],
        "added_date": "2025-01-16",
        "added_by": "admin@company.com"
      },
      {
        "email": "user3@email.com",
        "tier": "basic",
        "role": "viewer",
        "permissions": ["view"],
        "added_date": "2025-01-17",
        "added_by": "admin@company.com"
      }
    ]
  }
  ```
- **Payment Tiers:**
  - **Premium:** Full access (view, edit config, generate, manage all)
  - **Standard:** View + generate (no config editing)
  - **Basic:** View only (read-only, no generate)
- Multiple users can access the same newsletter with different tiers
- Admin manages user access via Admin Dashboard

---

### Step 4: Streamlit Cloud Deployment & User Access

**After configuration files are created:**

1. **Create Customer Configuration Files** in GitHub (completed in Step 3)

2. **Deploy Multi-Tenant Streamlit Cloud App (One-Time Setup - if not already deployed):**
   - Go to Streamlit Cloud dashboard
   - Create new app (or use existing if already deployed)
   - Connect to GitHub repository
   - Set main file: `streamlit_user_app.py`
   - Configure Streamlit secrets with shared values:
     ```toml
     github_repo = "org/newsletter-tool"
     github_token = "ghp_..."  # Admin/main GitHub token for accessing all customers
     admin_email = "admin@yourcompany.com"  # For user-customer mapping
     ```
   - **Note:** No `customer_id` in secrets - customer selection happens in-app
   - Deploy app (e.g., `newsletter-user.streamlit.app`)
   - **This is a one-time deployment** - all customers use the same app instance

3. **Grant User Access to Customer (Multi-User with Payment Tiers):**
   - In Admin Dashboard → Customer Management
   - Find customer (e.g., "acme", "htc", "apba")
   - Click "Manage User Access" or "User Access" tab
   - **Add user with tier and permissions:**
     - Enter user email address
     - Select payment tier: **Premium**, **Standard**, or **Basic**
     - System auto-assigns permissions based on tier:
       - **Premium:** Full access (view, edit config, generate, manage all)
       - **Standard:** View + generate (no config editing)
       - **Basic:** View only (read-only, no generate button)
   - Multiple users can be added to the same newsletter with different tiers
   - System updates `customers/{customer_id}/user_access.json` in GitHub with user details
   - User will now see this newsletter in their selector with appropriate permissions

4. **Provide Customer Access to User:**
   - Update customer record: Status = "Active"
   - Send welcome email with:
     - App URL: `https://newsletter-user.streamlit.app`
     - Instructions: "Select [Customer Name] from the newsletter selector when you log in"
     - Quick start guide
     - Support contact information

5. **User Experience:**
   - User opens app → Sees newsletter selector
   - Selector shows all newsletters they have access to (based on their email)
   - User selects newsletter (e.g., "HTC", "APBA") → App loads that customer's config and data
   - User can switch between newsletters they have access to at any time

6. **Post-Deployment:**
   - Monitor first-time user access
   - Verify users can see and access their newsletters
   - Update customer status if issues occur

---

## User App Core Functionality

The User App is a multi-tenant application where users find news articles and generate newsletters for different customers/brands. Users can switch between their accessible newsletters (e.g., HTC, APBA) within the same app. The interface is user-friendly with no technical jargon - background processes remain invisible to users.

### **Customer/Newsletter Selection & Switching**

**Multi-User Support: Multiple users can access the same newsletter with different permission levels based on payment tier.**

When users open the app:
- **Newsletter Selector:** Always visible in sidebar or header (available throughout app usage)
- Shows: Newsletter name (e.g., "HTC Global Newsletter", "APBA NewsBulletin"), customer logo/branding
- User selects newsletter → App loads that customer's configuration and data
- **User can switch newsletters at any time** during usage (not just at startup)
- Current newsletter context always visible (shows active newsletter name/branding)

**Permission-Based Features (Payment Tier):**
- **Premium Tier (Full Access):**
  - View articles, generate newsletters
  - Edit keywords and RSS feeds (Configuration tab editable)
  - Full access to all features
  
- **Standard Tier (Generate Access):**
  - View articles, generate newsletters
  - **Configuration tab read-only** (cannot edit keywords/feeds)
  
- **Basic Tier (View Only):**
  - View articles and generated newsletters
  - **No generate button** (cannot create newsletters)
  - **Configuration tab hidden** (no access to keywords/feeds)

**User Experience:**
- User with Premium access to HTC + Standard access to APBA sees:
  - Newsletter selector shows both HTC and APBA
  - When HTC selected: Full features available (edit config, generate)
  - When APBA selected: Limited features (generate only, config read-only)
  - Can switch between newsletters anytime

### Main Dashboard Features

#### **1. News Finding**

- **Finding News Articles:**
  - **Primary Method:** Google search for news articles based on configured keywords
  - **Secondary Method:** RSS feeds (configured by user)
  - Simple "Find News" button - no technical terms
  - Time period selector: "Last 7 days", "Last 14 days", "Last 30 days", etc.
  - Background processing - users see simple status: "Finding news..." → "Ready"
  - No technical details visible (no "scraping", "monitoring", "RSS", etc.)

- **Behind the Scenes (Invisible to User):**
  - Google News API or web scraping for news articles
  - RSS feed parsing
  - Article categorization based on keywords
  - Duplicate detection
  - Storage in database (not visible to users)

#### **2. Article Dashboard**

- **Article Display:**
  - List of found articles showing:
    - Article title (clickable link to full article)
    - Publication date
    - Source (news source name)
    - Category (auto-assigned from keywords)
    - **Article Preview:** Users can preview article content/excerpt before selecting
      - Expandable preview or modal popup
      - Shows article summary or first few paragraphs
      - "Select" button within preview
    - Used status (if article was already used in a newsletter)
  
- **Filtering & Search:**
  - Filter by category dropdown
  - Search articles by title/keyword
  - Time period selector (show articles from last N days)
  - Sort by date, category, or source

- **Article Selection:**
  - Select articles using checkboxes or selection buttons
  - Selected articles shown in summary panel
  - Selected count indicator
  - Remove from selection option
  - Only unused articles shown by default (option to show all)

#### **3. Newsletter Generation**

- **Direct Newsletter Creation:**
  - Select articles for newsletter (with preview capability)
  - Click "Generate Newsletter" button
  - **No Draft Step:** Newsletter generated directly from selected articles
  - Newsletter created immediately with:
    - Customer branding (title, footer, styling)
    - Articles categorized by category
    - Article titles, URLs, summaries
    - Week number in newsletter title
  - Selected articles automatically marked as "used"
  - Prevents duplicate selection in future newsletters

- **Newsletter Output:**
  - Formatted HTML newsletter displayed immediately
  - Download option (HTML format)
  - View newsletter content inline
  - Newsletter naming: `{short_name}_Newsletter_{timestamp}.html`
  - Saved to GitHub `data/newsletters/` folder (invisible to user)

#### **4. Configuration Tab**

- **Keywords Management:**
  - Simple interface to add/edit/delete keywords
  - Assign categories to keywords
  - Search and filter keywords
  - **Background Save:** Changes saved automatically to GitHub (no visible "saving" message needed)

- **Feeds Management:**
  - Simple interface to add/edit/delete RSS feed URLs
  - Assign categories to feeds
  - Enable/disable feeds
  - **Background Save:** Changes saved automatically to GitHub

### User App Tabs/Sections Structure:

```
User App Layout:
├── Dashboard (Main Tab)
│   ├── Find News Button & Time Period Selector
│   ├── Article Dashboard
│   │   ├── Available Articles (with preview capability)
│   │   ├── Article Preview Panel/Modal
│   │   └── Selected Articles Summary
│   ├── Generate Newsletter Button
│   └── Newsletter Output (displayed after generation)
├── Newsletters Tab
│   ├── List of Generated Newsletters
│   ├── Download Options
│   └── Newsletter Viewer
└── Configuration Tab
    ├── Keywords Editor
    └── Feeds Editor
```

### User Experience Principles:

- **No Technical Jargon:** Users see "Find News" not "RSS Monitoring" or "Scraping"
- **Background Processing:** All technical operations happen invisibly
- **Simple Status Indicators:** "Finding news...", "Ready", "Generating newsletter..."
- **Automatic Saving:** Configuration changes save automatically without user intervention
- **Article Preview:** Essential for users to decide which articles to include
- **Direct Newsletter Generation:** No intermediate drafts - one-click newsletter creation

---

## Customer-Specific Elements (Configurable)

### 1. **Titles / Headlines / Branding**

#### Configuration Structure:
```json
{
  "branding": {
    "company_name": "ACME Corporation",
    "short_name": "ACME",
    "application_name": "ACME Industry Newsletter",
    "newsletter_title_template": "{name} - Week {week}",
    "footer_text": "Brought to you by {company_name}",
    "footer_url": "https://www.acme.com",
    "footer_url_text": "www.acme.com"
  }
}
```

#### Code Impact:
- Dashboard header displays `branding.application_name`
- Newsletter titles use `branding.newsletter_title_template`
- Footer uses `branding.footer_text`, `footer_url`, `footer_url_text`

---

### 2. **Config Repository Content (User-Manageable)**

#### User Configuration Management in User App

Users need full control over their `keywords.json` and `feeds.json` files. This should be implemented as a dedicated **"Configuration"** tab or section in the User App.

#### Features Required:

1. **Keywords Manager:**
   - View all keyword → category mappings in an editable table
   - Add new keywords with category assignment
   - Edit existing keywords or categories
   - Delete keywords
   - Bulk import (optional: paste from Excel/CSV)
   - Search/filter keywords
   - Validation: Prevent duplicates, ensure required fields

2. **Feeds Manager:**
   - View all RSS feed URLs with their categories
   - Add new RSS feeds with category assignment
   - Edit feed URLs or categories
   - Enable/Disable feeds (without deleting)
   - Delete feeds
   - Test feed URL validity
   - Search/filter feeds
   - Validation: Check URL format, prevent duplicates

3. **Save Workflow:**
   - "Save Changes" button commits updates to GitHub
   - Shows confirmation message on successful save
   - Handles errors gracefully (network issues, validation failures)
   - Option to preview changes before saving
   - Auto-refresh after save to show current state

4. **UI Implementation:**
   - Use Streamlit `st.data_editor` for inline editing
   - Or custom form-based UI for better control
   - Tabbed interface: "Keywords" tab and "Feeds" tab
   - Clear save/cancel buttons
   - Status indicators (last saved, unsaved changes)

#### Technical Implementation:

```python
# Pseudo-code structure
def configuration_tab():
    st.header("📝 Configuration Management")
    
    tab1, tab2 = st.tabs(["Keywords", "RSS Feeds"])
    
    with tab1:
        keywords_manager()
    
    with tab2:
        feeds_manager()

def keywords_manager():
    # Load current keywords from GitHub
    keywords = load_keywords_from_github()
    
    # Display editable table
    edited_keywords = st.data_editor(
        keywords,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "term": st.column_config.TextColumn("Keyword"),
            "category": st.column_config.SelectboxColumn("Category", options=get_categories())
        }
    )
    
    if st.button("💾 Save Keywords"):
        if validate_keywords(edited_keywords):
            save_keywords_to_github(edited_keywords)
            st.success("Keywords saved successfully!")
        else:
            st.error("Validation failed. Please check your input.")
```

#### New Structure:
```
GitHub Repository Structure:
/customers/{customer_id}/
  ├── config/
  │   ├── keywords.json          # User-editable
  │   ├── feeds.json              # User-editable
  │   └── branding.json           # Admin-only
  └── data/
      ├── database.xlsx           # Customer-specific database
      └── newsletters/            # Generated newsletters
```

#### JSON Format Examples:

**keywords.json:**
```json
{
  "mappings": [
    {"term": "polyurethane", "category": "Materials"},
    {"term": "foam", "category": "Materials"},
    {"term": "sustainability", "category": "Industry News"}
  ]
}
```

**feeds.json:**
```json
{
  "feeds": [
    {
      "url": "https://example.com/rss",
      "category": "Industry News",
      "enabled": true,
      "last_scraped": null
    }
  ]
}
```

#### Code Locations:
- `htc_dashboard.py` - Line 34: `'config': BASE_DIR / "HTC_Config_Repository.xlsx"`
- `modules/formatter.py` - Line 41-50: `load_categories()` method
- `modules/monitor.py` - Feed loading and RSS parsing

---

### 3. **Downloads / File Naming**

#### Current State:
- **Newsletter Output:** `HTC_Newsletter_{timestamp}.html` (hardcoded)
- **Note:** Draft files exist in old tool but are internal processing step - not needed in new User App
- **Database:** `HTC_News_Database.xlsx` (hardcoded, but invisible to users)

#### New Structure:
```
File naming templates (configurable per customer):

newsletter_filename_template: "{customer_short_name}_Newsletter_{timestamp}.html"
database_filename: "{customer_id}_News_Database.xlsx"  (internal use only, not visible to users)
```

#### Configuration:
```json
{
  "file_naming": {
    "newsletter_template": "{short_name}_Newsletter_{timestamp}.html",
    "database_name": "{customer_id}_News_Database.xlsx"
  }
}
```

**Note:** No draft template needed - newsletter generated directly from selected articles.

#### Code Locations (Legacy - for reference only):
- `modules/formatter.py` - Line 188: `output_path = os.path.join(self.FORMATTED_FOLDER, f"HTC_Newsletter_{timestamp}.html")`
- `modules/formatter.py` - Line 199: Formatted newsletter pattern matching
- `htc_dashboard.py` - Line 35: Database path (internal storage, not visible to users)

**Note:** Draft file generation code (`modules/publisher.py` Line 81) is not needed in new User App - direct newsletter generation only.

---

### 4. **Additional Customer-Specific Elements Found**

#### **A. Footer Content (HTML Generated Newsletters)**
**Current:** Both apps hardcode `"Brought to you by HTC Global - www.htcglobal.asia"`

**Location:** `modules/formatter.py` - Line 147-149

**Configuration:**
```json
{
  "branding": {
    "footer_text": "Brought to you by {company_name}",
    "footer_url": "{company_website}",
    "footer_url_text": "{website_display}"
  }
}
```

#### **B. Logger Names**
**Current:** Both use `'HTC_Formatter'` as logger name

**Location:** `modules/formatter.py` - Line 28

**Configuration:**
```json
{
  "logging": {
    "logger_name": "{customer_id}_Formatter",
    "log_file": "{customer_id}_formatter.log"
  }
}
```

#### **C. Page Titles (HTML)**
**Current:** Dashboard HTML title hardcoded:
- HTC: `<title>HTC Global Newsletter</title>`
- APBA: `<title>APBA News Bulletin</title>`

**Location:** `templates/dashboard.html` - Line 4

**Configuration:** Use `branding.application_name` from config

---

## Configuration Management Architecture

### User-Facing Configuration (JSON) - In User App

**Location:** Separate "Configuration" tab or section in the User App

**Features:**

1. **Keywords Manager:**
   - View all keyword → category mappings
   - Add/Edit/Delete keyword → category mappings
   - Real-time validation
   - Search and filter functionality
   - Save to `config/keywords.json` in GitHub
   - Immediate feedback on save success/failure

2. **Feeds Manager:**
   - View all RSS feed URLs with categories
   - Add/Edit/Delete RSS feed URLs
   - Assign categories to feeds
   - Enable/Disable feeds (toggle on/off without deleting)
   - Test feed URL validity
   - Save to `config/feeds.json` in GitHub
   - Immediate feedback on save success/failure

**User Experience:**
- Changes are made locally first (in-memory)
- User reviews changes before saving
- "Save Changes" button commits to GitHub
- Confirmation message on success
- Error handling for network/GitHub issues
- Option to undo changes before saving (reset to last saved state)

### Admin Dashboard Visibility & Monitoring

**Critical Requirement:** Admin must have complete visibility into all customer activities and configurations.

#### **1. Configuration Visibility**

Admin can view/edit any customer's configuration repository:

- **View Customer Configs:**
  - Select customer from dropdown → view their complete config
  - Keywords: See all keyword → category mappings
  - Feeds: See all RSS feeds with categories and status
  - Branding: View company branding settings
  - File Naming: View filename templates

- **Configuration History:**
  - Track changes to keywords/feeds over time (via GitHub commit history)
  - See who made changes (if user tracking implemented)
  - When changes were made
  - Compare configurations across time points

- **Edit Customer Configs:**
  - Admin can edit any customer's keywords/feeds directly
  - Override customer changes if needed
  - Bulk edit capabilities

#### **2. Customer Activity Monitoring**

Admin can see all customer-generated content and activities:

- **Newsletters Created:**
  - List all newsletters generated by customer
  - View newsletter content
  - Download newsletters
  - See generation dates and frequency
  - See which articles were used in each newsletter

- **Article Finding Activity:**
  - View articles found in customer's database (internal storage)
  - See article sources and categories
  - Monitor news finding activity (Google News + RSS)
  - Track used/unused article status

- **Usage Statistics:**
  - Number of newsletters created
  - Most used keywords
  - Most active RSS feeds
  - Activity timeline
  - Config change frequency

#### **3. Cross-Customer Analytics**

Admin can analyze patterns across all customers:

- **Popular Keywords:** Most commonly used keywords across all customers
- **Popular Feeds:** Most frequently used RSS feeds
- **Usage Patterns:** Compare customer engagement levels
- **Trend Analysis:** How keywords/feeds evolve over time
- **Customer Health:** Identify inactive or highly active customers

#### **4. Admin Configuration Management (JSON + Excel Export/Import)**

1. **Branding Configuration:**
   - Admin-only access
   - Set company name, titles, footer for any customer
   - Save to `config/branding.json` in GitHub

2. **File Naming Configuration:**
   - Admin-only access
   - Define filename templates for any customer
   - Save to `config/file_naming.json` in GitHub

3. **Excel Export/Import:**
   - Admin can export all customer configs → Excel workbook (multiple sheets)
   - Export single customer or bulk export all customers
   - Admin can import Excel → update JSON configs
   - Enables bulk editing and backup
   - Comparative analysis in Excel

#### **5. Admin Dashboard Tabs/Sections (Complete Structure):**

```
Admin Dashboard Layout:
├── Overview Dashboard
│   ├── Key Metrics
│   │   ├── Total customers
│   │   ├── Active customers
│   │   ├── Inactive/suspended customers
│   │   ├── Total newsletters created (all time)
│   │   └── Revenue/subscription summary
│   ├── Recent Activity Feed
│   │   ├── New customer signups
│   │   ├── Recent newsletter generations
│   │   ├── Configuration changes
│   │   └── System alerts/warnings
│   └── Quick Actions
│       ├── Add New Customer
│       └── Export All Data
├── Customer Management
│   ├── Customer List View
│   │   ├── Table with columns:
│   │   │   - Customer ID
│   │   │   - Company Name
│   │   │   - Status (Active/Inactive/Suspended)
│   │   │   - Subscription Tier
│   │   │   - Created Date
│   │   │   - Last Activity
│   │   │   - Newsletter Count
│   │   │   - Actions (View/Edit/Delete)
│   │   ├── Search/Filter customers
│   │   └── Bulk actions (activate/deactivate)
│   ├── Customer Details Page
│   │   ├── Basic Information
│   │   │   - Customer ID (read-only)
│   │   │   - Company Name (editable)
│   │   │   - Short Name (editable)
│   │   │   - Contact Information (editable)
│   │   │   - Subscription Status (editable)
│   │   │   - Created Date
│   │   │   - Last Modified
│   │   ├── Account Status
│   │   │   - Active/Inactive toggle
│   │   │   - Suspension reason (if suspended)
│   │   │   - Subscription tier
│   │   │   - Renewal date
│   │   ├── Deployment Information
│   │   │   - Streamlit App URL
│   │   │   - GitHub folder path
│   │   │   - Deployment date
│   │   │   - Last deployment check
│   │   └── Statistics
│   │       - Total newsletters created
│   │       - Total articles found
│   │       - Keywords count
│   │       - Feeds count
│   │       - Last activity date
│   └── Customer Onboarding
│       ├── Start New Onboarding (Primary Method)
│       │   ├── Enter customer email
│       │   ├── Enter customer name (optional)
│       │   ├── Generate onboarding link
│       │   ├── Send email with link
│       │   └── Track invitation status
│       ├── Pending Onboarding Submissions
│       │   ├── List of customer submissions
│       │   ├── Review submission details
│       │   ├── Edit submission if needed
│       │   ├── Approve → Create customer account
│       │   └── Request changes → Email customer
│       └── Manual Entry (Fallback Method)
│           ├── Step 1: Basic Information
│           │   - Customer ID (validation: unique, lowercase, alphanumeric)
│           │   - Company Name
│           │   - Short Name
│           │   - Contact Email
│           │   - Contact Name
│           │   - Phone Number
│           ├── Step 2: Branding
│           │   - Application Name
│           │   - Newsletter Title Template
│           │   - Footer Text
│           │   - Footer URL
│           │   - Footer URL Display Text
│           ├── Step 3: Initial Keywords (Optional)
│           │   - Add keywords with categories
│           │   - Import from Excel/CSV
│           │   - Or leave empty for customer to populate
│           ├── Step 4: Initial Feeds (Optional)
│           │   - Add RSS feed URLs with categories
│           │   - Test feed URLs
│           │   - Or leave empty for customer to populate
│           ├── Step 5: Deployment Configuration
│           │   - Streamlit App URL (auto-suggest or manual)
│           │   - Deployment tier/plan
│           │   - Generate GitHub token instructions
│           ├── Step 6: Review & Confirm
│           │   - Preview all configuration
│           │   - Validate all inputs
│           │   - Create configuration files button
│           └── Step 7: Post-Deployment
│               - Show created config files
│               - Display Streamlit secrets template
│               - Provide deployment checklist
│               - Generate welcome email template
├── Configuration Viewer
│   ├── Customer Selector (dropdown)
│   ├── Keywords Tab
│   │   ├── View all keywords
│   │   ├── Edit keywords inline
│   │   ├── Add/Delete keywords
│   │   └── Export keywords
│   ├── Feeds Tab
│   │   ├── View all feeds
│   │   ├── Edit feeds inline
│   │   ├── Add/Delete feeds
│   │   ├── Test feed URLs
│   │   └── Export feeds
│   ├── Branding Tab
│   │   ├── View branding config
│   │   ├── Edit branding
│   │   └── Preview branding
│   └── Configuration History
│       ├── View GitHub commit history
│       ├── See who made changes
│       ├── Compare versions
│       └── Rollback to previous version
├── Activity Monitor
│   ├── All Newsletters (All Customers)
│   │   ├── Table with: Customer, Title, Date, Download
│   │   ├── Filter by customer/date
│   │   └── Preview newsletter content
│   ├── Newsletter Creation Activity
│   │   ├── Recent newsletters created
│   │   └── Newsletter content viewer
│   ├── Article Finding Activity
│   │   ├── Articles found (from Google News + RSS)
│   │   ├── Database size per customer
│   │   └── Duplicate detection alerts
│   └── Usage Statistics per Customer
│       ├── Newsletters created (time series)
│       ├── Articles found (time series)
│       ├── Config changes frequency
│       └── Activity heatmap
├── Analytics
│   ├── Cross-Customer Analytics
│   │   ├── Popular keywords (all customers)
│   │   ├── Popular feeds (all customers)
│   │   ├── Most active customers
│   │   └── Least active customers
│   ├── Trend Analysis
│   │   ├── Keyword usage trends
│   │   ├── Feed usage trends
│   │   └── Newsletter generation trends
│   └── Engagement Metrics
│       ├── Customer retention rates
│       ├── Average newsletters per customer
│       └── Feature usage statistics
└── Export/Import Tools
    ├── Export to Excel
    │   ├── Export all customer configs
    │   ├── Export single customer config
    │   └── Export analytics data
    ├── Import from Excel
    │   ├── Import keywords/feeds
    │   ├── Import customer data
    │   └── Bulk update configurations
    └── Bulk Operations
        ├── Bulk activate/deactivate customers
        ├── Bulk update branding
        └── Bulk export
```

---

## Streamlit Application Structure

### GitHub Repository Organization:
```
github.com/{org}/{newsletter-tool-repo}/
├── streamlit_user_app.py          # User-facing application (newsletter generation)
├── streamlit_admin_app.py         # Admin dashboard application
├── streamlit_onboarding_app.py    # Customer onboarding webpage (separate app)
├── config/
│   ├── customer_config.py         # Loads customer-specific configs from GitHub
│   ├── github_manager.py          # GitHub API integration
│   └── config_validator.py        # Validates JSON configs
├── modules/
│   ├── dashboard.py               # Main dashboard UI
│   ├── config_editor.py           # User config editing interface (keywords & feeds)
│   ├── config_manager.py          # GitHub read/write operations for config files
│   ├── news_finder.py             # Google News + RSS finding (customer-agnostic)
│   ├── formatter.py               # Newsletter formatting (uses config)
│   └── db.py                      # Database operations (uses config)
└── customers/
    ├── htc/
    ├── apba/
    └── {new_customer}/
```

### Application Separation:
- **User App:** 
  - Uses shared modules
  - Loads customer-specific config from GitHub
  - **Core Features:**
    - News finding (Google search + RSS feeds)
    - Article dashboard with preview capability
    - Direct newsletter generation (no draft step)
    - User-friendly interface (no technical terms)
  - **Configuration Tab:** Users can edit keywords and feeds
  - Background saving to GitHub (invisible to users)
  - All changes and generated content visible to admin via GitHub

- **Admin App:** 
  - Uses shared modules
  - Accesses all customer configs via GitHub
  - **Full visibility** into all customer activities:
    - View/edit any customer's config (including branding)
    - See all customer-generated newsletters
    - Monitor article finding activity and database
    - Track configuration change history
  - Excel export/import functionality
  - Cross-customer analytics and insights

### Configuration Loading Flow:
```
1. App starts → Load customer_id from Streamlit secrets
2. Fetch branding.json, keywords.json, feeds.json from GitHub
3. Merge into in-memory config object
4. All modules access config via customer_config.get_config()
```

---

## GitHub Repository Structure

### Multi-Customer Organization:
```
github.com/{org}/{newsletter-tool-repo}/
├── customers/
│   ├── htc/
│   │   ├── config/
│   │   │   ├── branding.json
│   │   │   ├── keywords.json
│   │   │   └── feeds.json
│   │   └── data/
│   │       ├── database.xlsx
│   │       └── newsletters/
│   ├── apba/
│   │   ├── config/
│   │   └── data/
│   └── {new_customer}/
│       ├── config/
│       └── data/
└── admin/
    └── config_export_import.py  # Admin tools
```

---

## Migration Steps

### Phase 1: Configuration Externalization
1. Create configuration schema (JSON structures)
2. Extract all hardcoded customer values to config files
3. Update code to read from config instead of hardcoded values
4. Test with existing HTC/APBA data

### Phase 2: GitHub Integration
1. Implement GitHub API client for reading/writing configs
2. Create Streamlit UI for JSON editing
3. Implement save/load operations via GitHub API
4. Test configuration updates

### Phase 3: Admin Dashboard
1. Create admin Streamlit app
2. Implement Excel export/import
3. Add analytics and cross-customer insights
4. Test admin workflows

### Phase 4: Streamlit Cloud Deployment
1. Prepare requirements.txt for Streamlit Cloud
2. Deploy User App: Set up Streamlit secrets per customer deployment
   - Each customer gets their own Streamlit Cloud instance (e.g., `htc-newsletter.streamlit.app`)
   - Each instance uses customer-specific secrets (customer_id, GitHub token)
3. Deploy Admin App: Single admin instance with access to all customers
   - Admin instance uses admin-level GitHub token with broader access
4. Configure GitHub repository access and permissions

---

**Note:** Detailed implementation specifications (function names, module structure, code architecture) should be documented in a separate **Implementation Plan** or **Development Guide** document. The design document focuses on WHAT needs to be built, while implementation details focus on HOW it's built.

---

## Technical Implementation Details

### Configuration Loader (`config/customer_config.py`):
```python
class CustomerConfig:
    def __init__(self, customer_id: str):
        self.customer_id = customer_id
        self.github_manager = GitHubManager()
        self.config_cache = {}
    
    def load_config(self):
        """Load all config files from GitHub and merge"""
        branding = self.github_manager.fetch_json(f"customers/{self.customer_id}/config/branding.json")
        keywords = self.github_manager.fetch_json(f"customers/{self.customer_id}/config/keywords.json")
        feeds = self.github_manager.fetch_json(f"customers/{self.customer_id}/config/feeds.json")
        
        return {
            "branding": branding,
            "keywords": keywords,
            "feeds": feeds,
            "file_naming": self._get_file_naming_config()
        }
    
    def _get_file_naming_config(self):
        """Generate file naming config from branding"""
        return {
            "newsletter_template": f"{self.config['branding']['short_name']}_Newsletter_{{timestamp}}.html",
            "draft_template": "draft_{timestamp}.xlsx",
            "database_name": f"{self.customer_id}_News_Database.xlsx"
        }
```

### Streamlit Secrets Structure:

**User App Secrets (per customer deployment):**
```toml
# .streamlit/secrets.toml (e.g., for HTC customer)
customer_id = "htc"
github_token = "ghp_..."  # Customer-specific token (read/write to their folder only)
github_repo = "org/newsletter-tool"
```

**Admin App Secrets (single admin deployment):**
```toml
# .streamlit/secrets.toml (admin instance)
admin_mode = true
github_token = "ghp_..."  # Admin token (full repo access)
github_repo = "org/newsletter-tool"
```

---

## Testing Strategy

### Unit Tests:
- Configuration loading and validation
- File naming template substitution
- Branding variable interpolation

### Integration Tests:
- GitHub API read/write operations
- Configuration update workflows
- Multi-customer config isolation

### User Acceptance Tests:
- Customer can edit keywords/feeds via UI
- Admin can export/import Excel configs
- Newsletter generation uses correct customer branding
- New customer onboarding creates all required config files

---

## Risk Mitigation

### Risk 1: GitHub API Rate Limits
**Mitigation:** Implement caching, batch operations, use GitHub App tokens with higher limits

### Risk 2: Config File Corruption
**Mitigation:** 
- JSON validation before save
- Git commit history for rollback
- Admin Excel export as backup

### Risk 3: Multi-Customer Config Conflicts
**Mitigation:** 
- Isolated customer directories in GitHub
- Customer ID validation in all operations
- Streamlit secrets per deployment prevent cross-customer access

---

## Future Enhancements

1. **Version Control UI:** View/edit config history in Streamlit
2. **Config Templates:** Pre-built configs for common customer types
3. **A/B Testing:** Test different branding/configs
4. **Multi-Language Support:** Customer-specific language settings
5. **Theme Customization:** CSS/styling per customer

---

## Admin Visibility Requirements

**Critical Requirement:** Admin must have complete visibility into all customer activities and configurations. This is not optional - it's a core requirement for monitoring, support, and business intelligence.

### What Admin Needs to See:

1. **Customer Configurations (Real-Time):**
   - ✅ View any customer's `keywords.json` (current state)
   - ✅ View any customer's `feeds.json` (current state)
   - ✅ View any customer's `branding.json`
   - ✅ View any customer's file naming config
   - ✅ Track configuration change history (via GitHub commits)

2. **Customer-Generated Content:**
   - ✅ All newsletters created by customer (from `data/newsletters/`)
   - ✅ Database entries (found articles stored in `data/database.xlsx`)
   - ✅ File creation timestamps
   - ✅ Content of newsletters

3. **Customer Activity Monitoring:**
   - ✅ When newsletters are created (timestamps)
   - ✅ When configs are changed (GitHub commit history)
   - ✅ When articles are found (news finding activity)
   - ✅ Which keywords are most frequently used
   - ✅ Which feeds are most active
   - ✅ Customer engagement patterns (active vs inactive)

4. **Cross-Customer Insights:**
   - ✅ Popular keywords across all customers
   - ✅ Popular feeds across all customers
   - ✅ Usage comparison between customers
   - ✅ Trends in keyword/feed usage over time

### Implementation Requirements:

- **Data Storage:** All customer data stored in GitHub is accessible to admin
- **Admin Access:** Admin app reads from same GitHub repository as customer apps
- **Permissions:** Admin has read/write access to all customer folders
- **History Tracking:** Configuration changes visible via GitHub commit history
- **File Locations:** Customer-generated files stored in customer's `data/` folder structure:
  ```
  customers/{customer_id}/
  ├── config/
  │   ├── keywords.json      ← Admin can view/edit
  │   ├── feeds.json         ← Admin can view/edit
  │   └── branding.json       ← Admin can view/edit
  └── data/
      ├── database.xlsx       ← Admin can view/download
      └── newsletters/        ← Admin can view/download
          └── {newsletter}.html
  ```

### Admin Dashboard Sections for Visibility:

1. **Customer Selector:** Dropdown to select any customer
2. **Config Viewer:** View/edit customer's keywords, feeds, branding
3. **Content Viewer:** Browse all newsletters and database entries
4. **Activity Timeline:** Chronological view of customer activities
5. **Analytics Dashboard:** Cross-customer insights and trends

---

## Customer Configuration Checklist

When onboarding a new customer, ensure the following are configured:

### Required During Onboarding:
- [ ] Customer ID assigned (lowercase, alphanumeric, unique)
- [ ] `branding.json` created with company information
- [ ] Initial `keywords.json` (can be empty, user will populate)
- [ ] Initial `feeds.json` (can be empty, user will populate)
- [ ] GitHub customer folder created: `customers/{customer_id}/`
- [ ] Streamlit Cloud app deployed with customer secrets
- [ ] Customer access URL provided
- [ ] Admin Dashboard configured to show new customer in selector

### Optional (Defaults Provided):
- [ ] Custom file naming templates
- [ ] Custom logging configuration
- [ ] Custom styling/theme

---

## Summary of Customer-Specific Elements

| Element | Configuration Source | When Set | User Editable |
|---------|---------------------|----------|---------------|
| Dashboard Header | `branding.json` → `application_name` | Onboarding | ❌ Admin only |
| Newsletter Title | `branding.json` → `newsletter_title_template` | Onboarding | ❌ Admin only |
| Footer Text/URL | `branding.json` → `footer_text`, `footer_url` | Onboarding | ❌ Admin only |
| Keywords | `keywords.json` | Onboarding (initial) | ✅ User can edit |
| RSS Feeds | `feeds.json` | Onboarding (initial) | ✅ User can edit |
| Newsletter Filename | `file_naming.json` (or default) | Onboarding | ❌ Admin only |
| Database Filename | `file_naming.json` (or default) | Onboarding | ❌ Admin only (internal use) |

---

## Document Revision History

- **2025-01-XX:** Initial design document created
- Based on analysis of HTC Newsletter Tool and APBA NewsBulletin codebases

