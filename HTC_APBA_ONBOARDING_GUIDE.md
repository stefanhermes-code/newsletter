# HTC & APBA Onboarding - Step-by-Step Guide

**Purpose:** Practical guide for onboarding HTC and APBA newsletters into the new Cloud system.

---

## Before You Start

### What You'll Need:

1. **Access to Admin App:** `gnp-backend.streamlit.app`
   - Admin username and password (set in Streamlit secrets)

2. **Information from Existing Tools:**
   - HTC Newsletter Tool folder
   - APBA NewsBulletin folder
   - Config files (if you want to migrate existing keywords/feeds)

3. **Customer Information:**
   - Your email address (will be the login for both newsletters)
   - Company details (HTC and APBA)

---

## Quick Start: Overview

You'll be creating **2 separate customer accounts**:
1. **HTC** (`customer_id: htc`)
2. **APBA** (`customer_id: apba`)

**Both will be accessible from the same User App** - you'll be able to switch between them.

---

## Part 1: Onboarding HTC Newsletter

### Step 1: Access Admin App

1. Go to: `gnp-backend.streamlit.app`
2. Login with admin credentials
3. You'll see the Overview Dashboard

### Step 2: Start Customer Onboarding

**Option A: From Overview Page**
- Click **"➕ Add New Customer"** button
- Automatically redirects to Customer Onboarding

**Option B: From Sidebar**
- Click **"Customer Onboarding"** in sidebar
- You'll see the onboarding wizard

### Step 3: Complete the 7-Step Wizard for HTC

#### **Step 1: Basic Information**

Enter:
- **Customer ID:** `htc` (lowercase, this is the folder name)
- **Company Name:** `HTC Global` (or full company name)
- **Short Name:** `HTC` (used in newsletter filenames)

Click **"Next →"**

#### **Step 2: Branding**

Enter:
- **Application Name:** `HTC Newsletter` (or whatever you call it)
- **Newsletter Title Template:** `{name} - Week {week}` (default is fine)
- **Footer Text:** Your company footer text
  - Example: `© 2025 HTC Global. All rights reserved.`
- **Footer URL:** Your company website URL
  - Example: `https://www.htcglobal.asia`
- **Footer URL Display Text:** `www.htcglobal.asia` (optional)

Click **"Next →"**

#### **Step 3: Keywords** (Optional - Can add later)

**Option A: Add keywords now**
- Enter keywords one by one, click **"➕ Add"** after each
- Example keywords:
  - `polyurethane`
  - `foam`
  - `sustainability`
  - `automotive`
  - `construction`
- (Add as many as you want)

**Option B: Skip for now**
- Check **"Skip keywords for now"**
- You can add them later in Configuration Viewer

Click **"Next →"**

#### **Step 4: RSS Feeds** (Optional - Can add later)

**Option A: Add feeds now**
- For each RSS feed:
  - **Feed Name:** `TechCrunch` (example)
  - **Feed URL:** `https://feeds.feedburner.com/oreilly/radar`
  - Click **"➕ Add Feed"**

**Option B: Skip for now**
- Check **"Skip feeds for now"**
- You can add them later in Configuration Viewer

Click **"Next →"**

#### **Step 5: Contact & Subscription Information**

Enter:
- **Contact Name:** `Stefan Hermes` (or your name)
- **Contact Email:** `stefan.hermes@htcglobal.asia` (your email - this becomes the login)
- **Subscription Tier:** `Premium` (for full access)
- **Phone Number:** (optional)

**Important:** The Contact Email automatically becomes the first user account for this newsletter.

Click **"Next →"**

#### **Step 6: Review**

Review all information:
- ✅ Check Customer ID is `htc`
- ✅ Check Company Name is correct
- ✅ Check Contact Email is correct (this is your login)
- ✅ Check branding information

**To Edit:** Click **"← Back"** to go to previous steps

**When Ready:** Click **"Next →"**

#### **Step 7: Create Customer Account**

1. Set **Initial Password:** `changeme123` (or your preferred password)
   - User will be able to change this later

2. Click **"Create Customer Account"** button

3. **Wait for creation:**
   - System creates folder structure in GitHub
   - Creates all configuration files
   - Creates user access file

4. **Success Message:**
   - Shows Customer ID
   - Shows initial user email and password
   - Customer can now log in!

**✅ HTC Newsletter Account Created!**

---

## Part 2: Onboarding APBA Newsletter

### Step 1: Start New Customer Onboarding

**From Admin Dashboard:**
- Go to **"Customer Management"** → Click **"➕ Add New Customer"**
- OR go to **"Customer Onboarding"** in sidebar

### Step 2: Complete the 7-Step Wizard for APBA

#### **Step 1: Basic Information**

Enter:
- **Customer ID:** `apba` (lowercase)
- **Company Name:** `APBA` (or full organization name)
- **Short Name:** `APBA`

Click **"Next →"**

#### **Step 2: Branding**

Enter:
- **Application Name:** `APBA NewsBulletin` (or whatever you call it)
- **Newsletter Title Template:** `{name} - Week {week}` (default is fine)
- **Footer Text:** Your APBA footer text
  - Example: `© 2025 APBA. All rights reserved.`
- **Footer URL:** Your APBA website URL (if applicable)
- **Footer URL Display Text:** (optional)

Click **"Next →"**

#### **Step 3: Keywords** (Optional)

Add APBA-specific keywords:
- `polyurethane` (if relevant)
- `foam industry` (if relevant)
- Add any APBA-specific terms

OR skip for now.

Click **"Next →"**

#### **Step 4: RSS Feeds** (Optional)

Add APBA-specific RSS feeds OR skip for now.

Click **"Next →"**

#### **Step 5: Contact & Subscription Information**

**Important:** Use the SAME email as HTC:
- **Contact Name:** `Stefan Hermes`
- **Contact Email:** `stefan.hermes@htcglobal.asia` (SAME EMAIL as HTC)
- **Subscription Tier:** `Premium`
- **Phone Number:** (optional)

**Why Same Email?**
- This allows you to access BOTH newsletters from the same User App account
- You'll see a dropdown to switch between HTC and APBA

Click **"Next →"**

#### **Step 6: Review**

Review all APBA information.

Click **"Next →"**

#### **Step 7: Create Customer Account**

1. Set **Initial Password:** (can be same or different)
2. Click **"Create Customer Account"**
3. Wait for success message

**✅ APBA Newsletter Account Created!**

---

## Part 3: Verifying Setup

### Check in Admin App:

1. **Go to "Customer Management"** → **"Customer List"**
2. You should see:
   - **HTC** (customer_id: `htc`)
   - **APBA** (customer_id: `apba`)

3. **Go to "Customer Management"** → **"User Access Management"**
4. Select `htc` customer:
   - Verify your email (`stefan.hermes@htcglobal.asia`) is listed
   - Tier should be `Premium`
5. Select `apba` customer:
   - Verify your email (`stefan.hermes@htcglobal.asia`) is listed
   - Tier should be `Premium`

### Check in User App:

1. Go to: `gnpuser.streamlit.app` (or your User App URL)
2. Login with:
   - **Email:** `stefan.hermes@htcglobal.asia`
   - **Password:** (the one you set during onboarding)
3. You should see:
   - A newsletter selector in the sidebar
   - Both **HTC Newsletter** and **APBA NewsBulletin** options
4. **Switch between newsletters:**
   - Select HTC from dropdown → See HTC branding, keywords, feeds
   - Select APBA from dropdown → See APBA branding, keywords, feeds

---

## Part 4: Adding Your Existing Keywords and Feeds

If you have existing keywords/feeds from your old tools:

### Method 1: Via Admin App (Configuration Viewer)

1. Go to **"Configuration Viewer"**
2. Select customer (`htc` or `apba`)
3. Go to **"Keywords"** tab:
   - Edit keywords in text area (one per line or comma-separated)
   - Click **"💾 Save Keywords"**
4. Go to **"RSS Feeds"** tab:
   - Add feeds one by one
   - OR import if you have a list

### Method 2: Via User App (If you have Premium tier)

1. Login to User App (`gnpuser.streamlit.app`)
2. Select newsletter (HTC or APBA)
3. Go to **"Configuration"** tab
4. Edit keywords and feeds
5. Changes save automatically in background

---

## Part 5: Migrating Existing Data (Optional)

If you want to migrate existing newsletters or databases:

### Newsletters:
- Existing newsletters in old folders stay where they are
- New newsletters will be saved to GitHub: `customers/{customer_id}/data/newsletters/`
- You can download old newsletters and re-upload if needed

### Keywords/Feeds:
- Open old `HTC_Config_Repository.xlsx`
- Copy keywords/feeds
- Paste into Admin App Configuration Viewer

---

## Troubleshooting

### "Customer ID already exists"
- You've already created this customer
- Check "Customer Management" → "Customer List"
- If you need to recreate, delete first (or use different ID)

### "Failed to create customer"
- Check GitHub connection (see Admin User Manual → Troubleshooting)
- Verify Streamlit secrets are set correctly
- Check GitHub token permissions

### "Can't see both newsletters in User App"
- Verify both customers have your email in `user_access.json`
- Check both customers are set to "Active" status
- Logout and login again to User App

### "Wrong branding/configuration"
- Edit via "Configuration Viewer" in Admin App
- Or edit via "Configuration" tab in User App (if Premium tier)

---

## Summary Checklist

After completing onboarding, verify:

- [ ] HTC customer created (`customer_id: htc`)
- [ ] APBA customer created (`customer_id: apba`)
- [ ] Your email added to both customers' user access
- [ ] Can login to User App
- [ ] Can see both newsletters in dropdown
- [ ] Can switch between HTC and APBA
- [ ] Branding shows correctly for each
- [ ] Keywords/feeds added (if applicable)
- [ ] Both customers show as "Active" in Admin App

---

## Next Steps

After onboarding:

1. **Test Newsletter Generation:**
   - Login to User App
   - Select HTC newsletter
   - Click "Find News"
   - Select articles
   - Generate newsletter
   - Verify it saves correctly

2. **Add More Keywords/Feeds:**
   - Use Configuration Viewer or User App
   - Add keywords from your old config files
   - Test news finding

3. **Add Additional Users** (if needed):
   - Admin App → Customer Management → User Access Management
   - Add users to HTC or APBA (or both)
   - Assign appropriate tiers

4. **Customize Branding:**
   - Adjust newsletter title templates
   - Update footer text/URLs
   - Make any branding changes

---

**Ready to Start?**

1. Login to Admin App: `gnp-backend.streamlit.app`
2. Click **"➕ Add New Customer"**
3. Follow the wizard for HTC (steps above)
4. Repeat for APBA
5. Verify in User App

**Good luck! 🚀**

