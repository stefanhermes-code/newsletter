# Admin Dashboard User Manual (GNP_Admin / gnp-backend)

**Version:** 1.0  
**Last Updated:** 2025-01-XX

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Login & Authentication](#login--authentication)
3. [Overview Dashboard](#overview-dashboard)
4. [Customer Management](#customer-management)
5. [Customer Onboarding](#customer-onboarding)
6. [Configuration Viewer](#configuration-viewer)
7. [Activity Monitoring](#activity-monitoring)
8. [Analytics](#analytics)
9. [Export/Import](#exportimport)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Accessing the Admin Dashboard

1. Navigate to your Admin App URL (e.g., `gnp-backend.streamlit.app`)
2. You will see the login page
3. Enter your admin credentials (see [Login & Authentication](#login--authentication))

### System Requirements

- **Web Browser:** Chrome, Firefox, Safari, or Edge (latest versions)
- **Internet Connection:** Required for GitHub access
- **Permissions:** Admin access credentials (configured in Streamlit secrets)

---

## Login & Authentication

### First-Time Login

The Admin App requires username and password authentication for security.

**Default Configuration:**
- **Username:** `admin` (configured in Streamlit secrets)
- **Password:** Set in Streamlit secrets as `admin_password`

### Login Process

1. Enter your **Username** in the login form
2. Enter your **Password** (input is hidden)
3. Click **"Login"** button
4. Upon successful login, you'll see the Admin Dashboard

### Logout

- Click the **"🚪 Logout"** button in the sidebar
- You will be redirected to the login page
- All session data will be cleared

### Security Notes

- **Never share your admin credentials**
- The password is stored securely in Streamlit secrets
- Each session is independent (logout on shared computers)

---

## Overview Dashboard

The Overview Dashboard provides a quick summary of your newsletter system.

### Key Metrics

The dashboard displays four main metrics:

1. **Total Customers** - Number of all customers in the system
2. **Active Customers** - Number of customers with "Active" status
3. **Total Newsletters** - Total number of newsletters generated (all customers)
4. **Pending Onboarding** - Number of pending onboarding submissions

### Recent Customers

The dashboard shows the **5 most recent customers** with:
- Company name
- Customer status (Active/Inactive)

### Quick Actions

**Add New Customer:**
- Click **"➕ Add New Customer"** button (available on Overview and Customer Management pages)
- Automatically redirects to Customer Onboarding wizard
- Start creating new customer immediately

**Customer Management:**
- Click **"👥 Customer Management"** button on Overview page
- Quick access to customer list and management

### Navigation

Use the sidebar to navigate between different sections:
- Overview
- Customer Management
- Customer Onboarding
- Configuration Viewer
- Activity Monitoring
- Analytics
- Export/Import

---

## Customer Management

The Customer Management section allows you to manage all customer accounts, view details, and manage user access.

### Customer List Tab

**Features:**
- **Add New Customer** button (redirects to Customer Onboarding)
- View all customers in an expandable list
- Search customers by name, ID, or email
- Filter customers by status (All, Active, Inactive)
- Quick actions: View Details, Manage Users

**Add New Customer:**
- Click **"➕ Add New Customer"** button at the top
- Automatically redirects to Customer Onboarding page
- Start creating new customer immediately

**How to Use:**

1. **Search Customers:**
   - Enter text in the "Search Customers" field
   - Searches in: Customer ID, Company Name, Contact Email
   - Results update automatically

2. **Filter by Status:**
   - Use the dropdown to filter by:
     - **All** - Show all customers
     - **Active** - Show only active customers
     - **Inactive** - Show only inactive customers

3. **View Customer Info:**
   - Expand any customer card to see:
     - Status (Active/Inactive)
     - Customer ID
     - Contact Email
     - Subscription Tier
   - Click **"View Details"** to see full information
   - Click **"Manage Users"** to access user management

### Customer Details Tab

**Features:**
- View complete customer information
- See configuration summary (keywords count, feeds count, users count)

**How to Use:**

1. **Select Customer:**
   - Use the dropdown to select a customer
   - If you came from Customer List, the selected customer is pre-filled

2. **View Information:**
   - **Basic Information:**
     - Customer ID
     - Company Name
     - Status
     - Created Date
   - **Contact Information:**
     - Contact Name
     - Contact Email
     - Phone Number
     - Subscription Tier
   - **Configuration Summary:**
     - Number of Keywords configured
     - Number of RSS Feeds configured
     - Number of Users with access

### User Access Management Tab

**Features:**
- View all users with access to a customer
- Add new users
- Update user tiers (Premium/Standard/Basic)
- Remove user access

**How to Use:**

1. **Select Customer:**
   - Choose a customer from the dropdown

2. **View Users:**
   - Each user is shown in an expandable card with:
     - Email address
     - Payment Tier (Premium/Standard/Basic)
     - Role (admin/editor/viewer)
     - Status (Active/Inactive)
     - Valid Until date (if set)

3. **Change User Tier:**
   - Select new tier from dropdown
   - Click **"Update Tier"** button
   - Permissions update automatically:
     - **Premium:** Full access (view, edit, generate, manage_config)
     - **Standard:** View + generate
     - **Basic:** View only

4. **Remove User:**
   - Click **"Remove User"** button
   - User will lose access immediately
   - Action cannot be undone (but you can re-add the user)

5. **Add New User:**
   - Fill in the form:
     - **Email Address** (required)
     - **Tier** (Premium/Standard/Basic)
     - **Role** (admin/editor/viewer)
     - **Initial Password** (default: "changeme123")
   - Click **"Add User"** button
   - User can now log in to the User App

**Important Notes:**
- Users should change their password after first login (via User App Settings)
- Tier determines permissions automatically
- Role is informational (doesn't affect permissions directly)

---

## Customer Onboarding

The Customer Onboarding wizard allows you to create new customer accounts step-by-step.

### Onboarding Process

The wizard consists of **7 steps**:

1. **Basic Information**
2. **Branding**
3. **Keywords** (Optional)
4. **RSS Feeds** (Optional)
5. **Contact Information**
6. **Review**
7. **Create Account**

### Step 1: Basic Information

**Required Fields:**
- **Customer ID** * - Lowercase, alphanumeric only (e.g., "acme", "htc", "apba")
  - Used as folder name in GitHub
  - Must be unique
- **Company Name** * - Full company name
- **Short Name** * - Used in file names (e.g., "ACME", "HTC")

**Tips:**
- Customer ID should be simple and descriptive
- Short Name appears in newsletter filenames

### Step 2: Branding

**Required Fields:**
- **Application Name** * - What the newsletter will be called (e.g., "ACME Industry Newsletter")
- **Footer Text** * - Text that appears at bottom of newsletters
- **Footer URL** * - Company website URL

**Optional Fields:**
- **Newsletter Title Template** - Default: `{name} - Week {week}`
  - Use `{name}` and `{week}` as placeholders
  - Example: "ACME Newsletter - Week 5"
- **Footer URL Display Text** - Display text for footer link

### Step 3: Keywords (Optional)

**Purpose:** Initial keywords for Google News searches

**How to Add Keywords:**
1. Enter keyword in text input
2. Click **"➕ Add"** button
3. Keywords appear in a list below
4. Click **"🗑️"** to remove a keyword

**Skip Option:**
- Check "Skip keywords for now" to add them later
- Keywords can be added anytime via Configuration Viewer

**Tips:**
- Add 5-10 relevant keywords initially
- Can be edited later by admin or Premium users

### Step 4: RSS Feeds (Optional)

**Purpose:** Initial RSS feeds for news finding (secondary source)

**How to Add Feeds:**
1. Enter **Feed Name** (e.g., "TechCrunch")
2. Enter **Feed URL** (must start with http:// or https://)
3. Click **"➕ Add Feed"** button
4. Feed appears in list below
5. Click **"🗑️ Delete"** to remove

**Skip Option:**
- Check "Skip feeds for now" to add them later
- Feeds can be added anytime via Configuration Viewer

**Tips:**
- Test feed URLs before adding
- RSS feeds are secondary to Google News
- Can be enabled/disabled per feed

### Step 5: Contact & Subscription Information

**Required Fields:**
- **Contact Name** * - Primary contact person
- **Contact Email** * - Will become the initial user account
- **Subscription Tier** * - Determines user permissions
  - **Premium:** Full access
  - **Standard:** View + generate
  - **Basic:** View only

**Optional Fields:**
- **Phone Number** - Contact phone

**Important:**
- Contact Email automatically becomes the first user
- Initial password will be set in Step 7

### Step 6: Review

**Purpose:** Review all information before creating account

**What to Check:**
- All required fields are filled
- Customer ID is unique and correct
- Contact email is correct (this becomes the login)
- Branding information looks correct
- Keywords and feeds (if added) are correct

**Actions:**
- Use **"← Back"** to edit any step
- Continue to Step 7 to create account

### Step 7: Create Customer Account

**Validation:**
- System checks all required fields
- Shows warning if anything is missing

**Initial Password:**
- Set initial password for contact email user
- Default: "changeme123" (can be changed)
- User should change password after first login

**What Happens When You Click "Create Customer Account":**

1. ✅ **Validates** all information
2. **Creates** customer folder structure in GitHub
3. **Generates** configuration files:
   - `branding.json`
   - `keywords.json` (if keywords provided)
   - `feeds.json` (if feeds provided)
   - `customer_info.json`
   - `user_access.json` (with initial user)
4. **Adds** customer to system
5. **Shows success message** with:
   - Customer ID
   - Initial user email and password

**After Creation:**
- Customer can immediately log in to User App
- All configurations are saved to GitHub
- Admin can view/edit via Configuration Viewer

---

## Configuration Viewer

The Configuration Viewer allows you to view and edit customer configurations.

### Accessing Configurations

1. Select a customer from the dropdown
2. Navigate between tabs:
   - **Keywords** - Edit keywords
   - **RSS Feeds** - Edit feeds
   - **Branding** - Edit branding
   - **History** - View change history

### Keywords Tab

**View Keywords:**
- See all current keywords in a formatted list
- Keyword count displayed

**Edit Keywords:**
1. Keywords appear in a text area (one per line)
2. Edit directly in the text area:
   - One keyword per line, OR
   - Comma-separated keywords
3. Click **"💾 Save Keywords"** button
4. Changes saved to GitHub immediately

**Tips:**
- Duplicates are automatically removed
- Case-insensitive duplicate detection
- Empty lines are ignored

### RSS Feeds Tab

**View Feeds:**
- All feeds displayed in expandable cards
- Shows: Name, URL, Enabled status

**Edit Existing Feed:**
1. Expand feed card
2. Edit **Feed Name** and/or **Feed URL**
3. Toggle **Enabled** checkbox
4. Click **"💾 Update"** button

**Delete Feed:**
- Click **"🗑️ Delete"** button in feed card

**Add New Feed:**
1. Enter **Feed Name**
2. Enter **Feed URL** (must start with http:// or https://)
3. Click **"➕ Add Feed"** button

### Branding Tab

**Edit Branding:**
1. All branding fields in one form:
   - Application Name
   - Short Name
   - Newsletter Title Template
   - Footer Text
   - Footer URL
   - Footer URL Display Text
2. Make changes
3. Click **"💾 Save Branding"** button
4. Changes apply immediately to customer's newsletters

**Important:**
- Title Template uses `{name}` and `{week}` placeholders
- Footer URL must be a valid URL

### History Tab

**View Change History:**
- Shows last 20 configuration changes
- Displays:
  - Configuration file name (keywords.json, feeds.json, branding.json)
  - Commit message
  - Author
  - Date/Time
  - Link to view on GitHub

**Use Cases:**
- Track who made changes
- See when configurations were updated
- Rollback to previous versions (via GitHub if needed)

---

## Activity Monitoring

Monitor customer activities including newsletter generation and configuration changes.

### Customer Activity View

**Select Customer:**
- Choose "All Customers" for system-wide view
- Or select specific customer

### Newsletters Tab

**View Newsletter Activity:**
- Lists all newsletters generated by customer
- Sorted by date (newest first)

**For Each Newsletter:**
- **Filename** - Newsletter filename
- **Size** - File size in bytes
- **Last Modified** - When it was created/modified
- **Actions:**
  - **👁️ View** - Preview newsletter HTML in browser
  - **📥 Download** - Download newsletter HTML file

**Statistics:**
- Total newsletter count
- Latest newsletter date

### Configuration Changes Tab

**View Configuration History:**
- Shows all configuration file changes
- Includes: keywords.json, feeds.json, branding.json, user_access.json

**For Each Change:**
- **Configuration File** - Which file was changed
- **Commit Message** - What was changed
- **Author** - Who made the change
- **Date** - When it was changed
- **GitHub Link** - View commit on GitHub

**Use Cases:**
- Monitor customer activity
- Track configuration changes
- Audit trail for customer actions

### All Customers Activity

**Summary Metrics:**
- Total Customers
- Active Customers (with newsletters)
- Total Newsletters (across all customers)
- Average Newsletters per Customer

**Customer List:**
- Each customer shows:
  - Company Name
  - Newsletter Count
  - Quick stats (Keywords, Feeds, Users)
- Click **"View Details"** to see full activity

---

## Analytics

Cross-customer analytics and insights.

### Usage Patterns Tab

**Top Keywords:**
- Lists most popular keywords across all customers
- Shows how many customers use each keyword
- Sorted by usage count

**Top RSS Feeds:**
- Lists most popular RSS feeds across all customers
- Shows how many customers use each feed
- Sorted by usage count

**Most Active Customers:**
- Lists customers by newsletter generation activity
- Shows newsletter count for each customer
- Sorted by activity (most active first)

**Use Cases:**
- Identify popular keywords/feeds
- See which customers are most engaged
- Plan feature improvements based on usage

### Trend Analysis Tab

**Key Metrics:**
- **Customer Retention Rate** - Percentage of active customers
- **Active Customers** - Current active customer count
- **Total Users** - Total users across all customers

**Subscription Tier Distribution:**
- Shows distribution of payment tiers
- Helps understand customer base composition

**Use Cases:**
- Track business metrics
- Understand customer base
- Identify trends

---

## Export/Import

Export customer configurations to Excel or import from Excel files.

### Export Section

**Export All Configurations:**
1. Select **"All Customers"** option
2. Click **"📥 Export All Configs to Excel"** button
3. Wait for export to complete
4. Click **"📥 Download Excel File"** button
5. File downloads with name: `all_customer_configs_YYYYMMDD_HHMMSS.xlsx`

**Export Single Customer:**
1. Select **"Single Customer"** option
2. Choose customer from dropdown
3. Click **"📥 Export Customer Config"** button
4. Wait for export
5. Download file: `{customer_id}_config_YYYYMMDD_HHMMSS.xlsx`

**Excel File Structure:**
- **Sheet 1: Customers** - Customer information
- **Sheet 2: Keywords** - All keywords (customer + keyword)
- **Sheet 3: RSS Feeds** - All feeds (customer + feed details)
- **Sheet 4: Branding** - All branding configurations

### Import Section

**Import Process:**
1. Click **"Upload Excel File"** button
2. Select Excel file (`.xlsx` format)
3. File preview shows first 20 rows
4. Review data
5. Click **"📤 Import Configs"** button
6. System imports all data:
   - Updates customer info
   - Updates keywords
   - Updates RSS feeds
   - Updates branding

**Import Results:**
- Shows number of configurations imported
- Lists any errors encountered
- Each successful import counted

**Use Cases:**
- Backup customer configurations
- Bulk update configurations
- Migrate data between systems
- Create configuration templates

**Important Notes:**
- Import overwrites existing configurations
- Always export first as backup
- Verify data before importing

---

## Troubleshooting

### Common Issues

#### "Failed to connect to GitHub"
**Problem:** App can't connect to GitHub repository

**Solutions:**
1. Check Streamlit secrets:
   - `github_token` is set correctly
   - `github_repo` is `"stefanhermes-code/newsletter"`
2. Verify GitHub token has `repo` permissions
3. Check GitHub token hasn't expired
4. Verify repository exists and is accessible

#### "Admin password not configured"
**Problem:** Can't log in to Admin App

**Solutions:**
1. Go to Streamlit Cloud → Settings → Secrets
2. Add `admin_username` (default: "admin")
3. Add `admin_password` (set a secure password)
4. Save secrets
5. App will restart automatically

#### "Customer not found"
**Problem:** Customer ID doesn't exist

**Solutions:**
1. Check customer exists in Customer List
2. Verify customer folder exists in GitHub
3. Use Customer Onboarding to create customer

#### "Failed to save configuration"
**Problem:** Can't save changes

**Solutions:**
1. Check GitHub connection
2. Verify GitHub token permissions
3. Check for merge conflicts (may need to pull first)
4. Try again (might be temporary network issue)

#### "No customers found"
**Problem:** Customer list is empty

**Solutions:**
1. Create first customer via Customer Onboarding
2. Check GitHub repository has `customers/` folder
3. Verify GitHub connection is working

---

## Best Practices

### Customer Management

1. **Use Descriptive Customer IDs**
   - Keep them short but meaningful
   - Lowercase, alphanumeric only
   - Example: "acme" not "ACME_Company_Newsletter_2025"

2. **Verify Contact Email**
   - Contact email becomes login account
   - User receives this as their login
   - Can't be easily changed later

3. **Set Strong Initial Passwords**
   - Don't use "changeme123" in production
   - Users should change password immediately
   - Consider password requirements

### User Access Management

1. **Assign Appropriate Tiers**
   - Premium for customers who need full control
   - Standard for most customers (view + generate)
   - Basic for read-only access

2. **Regular Access Reviews**
   - Periodically review user lists
   - Remove inactive users
   - Update tiers as needed

3. **Track User Changes**
   - Monitor user access changes
   - Keep audit trail via Activity Monitoring

### Configuration Management

1. **Test Before Bulk Changes**
   - Test configuration changes on one customer first
   - Verify changes work as expected
   - Then apply to multiple customers if needed

2. **Use Export/Import Carefully**
   - Always export before importing
   - Review Excel file before importing
   - Import overwrites existing data

3. **Monitor Change History**
   - Regularly check History tab
   - Track who made changes
   - Identify unexpected changes quickly

---

## Support

For issues or questions:

1. **Check Troubleshooting section** above
2. **Review Activity Monitoring** for error patterns
3. **Check GitHub repository** for file issues
4. **Verify Streamlit secrets** are configured correctly

---

**End of Manual**

