# Customer Onboarding Process - Practical Guide

**Purpose:** This guide explains the practical, step-by-step process for onboarding new customers to the Newsletter Tool Cloud.

---

## Overview: How Onboarding Works

When a new customer subscribes, you (the admin) need to:
1. **Collect information** from the customer (via conversation, email, or form)
2. **Enter information** into the Admin Dashboard's onboarding wizard
3. **System creates** all configuration files automatically
4. **Deploy** the customer's Streamlit app
5. **Provide access** to the customer

---

## How to Gather Information from Customers

### **Method 1: Customer Onboarding Webpage (Primary - Recommended)**

**This is the most streamlined approach - automated and professional:**

#### **How It Works:**

1. **Admin Initiates from Admin Dashboard:**
   - Go to Admin Dashboard → "Customer Management" → "Start Onboarding"
   - Enter customer email address
   - Click "Send Onboarding Link"
   - System generates unique onboarding link
   - System sends email to customer with link

2. **Customer Receives Email:**
   - Email contains: Personalized onboarding link
   - Link is unique and time-limited (e.g., valid for 7 days)
   - Link goes to: `onboarding.streamlit.app/start?token={unique_token}`

3. **Customer Fills Out Form:**
   - Customer clicks link
   - Opens streamlined onboarding webpage
   - Step-by-step form (same 7 steps as admin wizard)
   - All fields with helpful placeholders and examples
   - Can save progress and return later (using token)
   - Submit when complete

4. **Admin Reviews Submission:**
   - Customer's submission appears in Admin Dashboard
   - Status: "Pending Review"
   - Admin can review, edit if needed
   - Admin approves → System creates config files automatically
   - Admin can reject/request changes

#### **Benefits:**
- ✅ Professional, branded experience for customer
- ✅ No back-and-forth emails
- ✅ Structured data collection
- ✅ Admin can review before creating
- ✅ Automatic reminder if customer doesn't complete

---

### **Method 2: Email/Form Template (Fallback)**

**Use this method if:**
- Email sending is not configured/available
- Customer prefers traditional email communication
- Onboarding webpage has technical issues

If customer prefers or webpage not available:

Send the customer an onboarding form via email:

**Onboarding Information Request Template:**

```
Subject: Newsletter Tool Setup - Information Needed

Dear [Customer Name],

To set up your personalized Newsletter Tool, please provide the following information:

**Company Information:**
- Company Name: _______________
- Short Name (for files/naming): _______________

**Newsletter Branding:**
- What should your newsletter be called? _______________
- Footer text: _______________
- Company website URL: _______________

**News Topics:**
- What topics/terms should we search for? (comma-separated)
  Example: polyurethane, foam, sustainability
  Your topics: _______________

- How should these be categorized?
  Example: polyurethane → Materials, sustainability → Industry News
  Your categories: _______________

**Optional - RSS Feeds:**
- Any specific RSS feeds you want included?
  URLs: _______________

**Contact Information:**
- Primary contact: _______________
- Email: _______________
- Phone: _______________

Thank you!
```

---

## Email Sending Requirements & Setup

**⚠️ Important:** The Customer Onboarding Webpage method (Method 1) requires email sending capability. This section explains how to set it up.

### **Email Sending Options:**

#### **Option A: SMTP (Simple Mail Transfer Protocol) - Recommended**

**How It Works:**
- Use Python's built-in `smtplib` library
- Configure SMTP server credentials in Streamlit Secrets
- Send emails via your existing email account (Gmail, Outlook, etc.) or dedicated SMTP service

**Setup Steps:**

1. **Get SMTP Credentials:**
   - **Gmail:** Enable "App Password" in Google Account settings
   - **Outlook/Office 365:** Use app password or OAuth
   - **Custom SMTP:** Get server address, port, username, password from email provider

2. **Configure Streamlit Secrets:**
   - Go to Streamlit Cloud → Admin App → Settings → Secrets
   - Add SMTP configuration:
   ```toml
   [email]
   smtp_server = "smtp.gmail.com"  # or your SMTP server
   smtp_port = 587
   smtp_username = "your-email@gmail.com"
   smtp_password = "your-app-password"
   from_email = "noreply@yourcompany.com"
   from_name = "Newsletter Tool"
   ```

3. **Code Implementation:**
   - Module: `admin_modules/email_sender.py`
   - Functions: `send_onboarding_email()`, `send_welcome_email()`, etc.

**Pros:**
- ✅ Free (if using Gmail/Outlook)
- ✅ Simple setup
- ✅ Works with most email providers

**Cons:**
- ❌ Gmail has daily sending limits (~500 emails/day)
- ❌ Requires app password (two-factor authentication)
- ❌ May be marked as spam if not configured properly

---

#### **Option B: Third-Party Email Service (Professional)**

**Recommended Services:**
- **SendGrid** (Free tier: 100 emails/day)
- **Mailgun** (Free tier: 5,000 emails/month)
- **AWS SES** (Very cheap, ~$0.10 per 1,000 emails)
- **Mailjet** (Free tier: 200 emails/day)

**Setup Steps:**

1. **Sign up for service** (e.g., SendGrid)
2. **Get API key** from service dashboard
3. **Configure Streamlit Secrets:**
   ```toml
   [email]
   service = "sendgrid"  # or "mailgun", "ses", etc.
   api_key = "SG.xxxxxxxxxxxxx"
   from_email = "noreply@yourcompany.com"
   from_name = "Newsletter Tool"
   ```

4. **Install Python Package:**
   ```python
   # For SendGrid
   pip install sendgrid
   
   # For Mailgun
   pip install mailgun
   
   # For AWS SES
   pip install boto3
   ```

**Pros:**
- ✅ Higher sending limits
- ✅ Better deliverability (less spam)
- ✅ Analytics and tracking
- ✅ Professional appearance

**Cons:**
- ❌ Free tiers have limits
- ❌ May require paid plan for high volume
- ❌ Additional dependency

---

#### **Option C: Streamlit Cloud + Custom Domain Email (Advanced)**

**How It Works:**
- Use your own email server/domain
- Configure MX records
- More professional, no third-party dependency

**Pros:**
- ✅ Professional appearance
- ✅ No sending limits (based on your server)
- ✅ Full control

**Cons:**
- ❌ Requires email server setup
- ❌ More complex configuration
- ❌ Server maintenance required

---

### **Email Sending Implementation:**

**Required Functions:**
- `send_onboarding_email(email, token, link)` - Send onboarding invitation
- `send_welcome_email(customer_id, app_url)` - Send welcome email after deployment
- `send_submission_notification(admin_email, customer_email)` - Notify admin of new submission

**Fallback Strategy:**
- If email sending fails, admin can manually copy onboarding link
- Display link in Admin Dashboard for manual sharing
- Admin can send link via their own email client

---

### **Testing Email Sending:**

**Before going live:**
1. Test onboarding email sending from Admin Dashboard
2. Verify email arrives in inbox (check spam folder)
3. Test email link works correctly
4. Verify all email templates render properly

**Troubleshooting:**
- Check Streamlit secrets are correct
- Verify SMTP server/API credentials
- Check firewall/network restrictions
- Review email service logs for errors

---

## Practical Onboarding Process (Step-by-Step)

### **Method 1: Customer Onboarding Webpage (Primary Flow)**

### **Phase 1: Initiate Onboarding from Admin Dashboard**

**Step 1: Start Onboarding Process**
- Go to Admin Dashboard → "Customer Management" tab
- Click "Start New Customer Onboarding" button
- Enter customer email address
- Optionally enter customer name (for personalized email)
- Click "Send Onboarding Link"

**What Happens:**
- System generates unique onboarding token
- System creates temporary onboarding record (status: "Invitation Sent")
- System sends email to customer with personalized link
- Link format: `onboarding.streamlit.app/start?token={unique_token}&email={customer_email}`

**Email Template (Auto-sent):**
```
Subject: Set Up Your Newsletter Tool - Action Required

Dear [Customer Name],

Welcome! Your personalized Newsletter Tool is ready to be configured.

Click here to set up your account:
[ONBOARDING LINK - Click to Start]

This link is valid for 7 days.

The setup takes about 10-15 minutes. You can save your progress and return later if needed.

Need help? Contact us at [support email]

Best regards,
[Your Company Name]
```

---

### **Phase 2: Customer Completes Onboarding Form**

**Customer's Experience:**

1. **Customer clicks link** → Opens onboarding webpage
2. **Onboarding Webpage Structure:**
   - Welcome screen with progress indicator
   - Same 7 steps as admin wizard, but customer-facing
   - Each step clearly explained
   - Can navigate back/forward
   - "Save Progress" button (auto-saves)
   - "Submit" button at the end

3. **Form Steps (Customer-Friendly):**

   **Step 1: Company Information**
   - Company Name: [text input]
   - Short Name (for file naming): [text input]
   - Help text: "Short name will be used in file names"
   
   **Step 2: Newsletter Branding**
   - What should your newsletter be called? [text input]
   - Example: "ACME Industry Newsletter"
   - Footer text: [text input]
   - Your website URL: [text input]
   - Help text: "This appears at the bottom of each newsletter"
   
   **Step 3: News Topics (Optional)**
   - What topics should we search for?
   - Add keywords: [text input] → Category: [dropdown]
   - Can add multiple keywords
   - Help text: "You can add more later in the app"
   - "Skip this step" button available
   
   **Step 4: News Sources (Optional)**
   - Any RSS feeds you want included?
   - Feed URL: [text input] → Category: [dropdown]
   - "Test Feed" button to verify
   - "Skip this step" button available
   
   **Step 5: Contact Information**
   - Your Name: [text input]
   - Phone Number: [text input]
   - Email: [pre-filled, read-only]
   
   **Step 6: Review**
   - Preview all your information
   - Edit any section if needed
   
   **Step 7: Submit**
   - Click "Submit Onboarding Information"
   - Confirmation message: "Thank you! We'll review and set up your account shortly."

4. **What Happens After Customer Submits:**
   - Submission saved with status: "Pending Review"
   - Email notification sent to admin: "New onboarding submission from [customer email]"
   - Customer sees: "Your information has been received. We'll contact you when your account is ready (typically within 24 hours)."

---

### **Phase 3: Admin Reviews & Approves**

**Step 1: Receive Notification**
- Admin gets email: "New customer onboarding submission"
- Or see notification in Admin Dashboard

**Step 2: Review Submission**
- Go to Admin Dashboard → "Customer Management" → "Pending Onboarding"
- Click on customer submission
- Review all information
- **Option A:** Approve as-is → Click "Create Customer Account"
- **Option B:** Edit information → Make changes → Then approve
- **Option C:** Request changes → Send email to customer with notes

**Step 3: System Creates Configuration**
- When admin clicks "Create Customer Account":
  - System validates all information
  - Creates customer ID (auto-generated or admin can set)
  - Creates all config files in GitHub automatically
  - Same process as manual admin entry (Step 3 in Method B below)
  - Generates Streamlit secrets template
  - Status changes to: "Configuration Created - Ready for Deployment"

---

### **Phase 4: Deploy & Provide Access**
- Same as Method B, Phase 3 below

---

### **Method B: Manual Admin Entry (Alternative Flow)**

### **Phase 1: Information Gathering**

**When:** During sales call, onboarding meeting, or customer fills out form

**What You Need:**
- Pen & paper, or document template
- Access to customer's website (for branding details)

**Information to Collect:**
- ✅ Company name & short name
- ✅ Contact details (name, email, phone)
- ✅ Newsletter branding preferences
- ✅ Initial keywords they want to search for
- ✅ How to categorize those keywords
- ✅ Any RSS feeds they want included (optional)
- ✅ Subscription details

---

### **Phase 2: Enter Information into Admin Dashboard**

**Step 1: Open Admin Dashboard**
- Navigate to: `newsletter-admin.streamlit.app`
- Go to "Customer Management" tab
- Click "Add New Customer"

**Step 2: Fill Out Onboarding Wizard**

The wizard has 7 steps:

#### **Wizard Step 1: Basic Information**
- Customer ID: Type a short identifier (e.g., "acme")
  - System checks if it's unique automatically
  - Must be lowercase, alphanumeric only
- Company Name: Full company name
- Short Name: Short version for filenames
- Contact Email: Customer's email
- Contact Name: Primary contact person
- Phone Number: Contact phone

#### **Wizard Step 2: Branding**
- Application Name: What appears at top of dashboard
  - Example: "ACME Industry Newsletter"
- Newsletter Title Template: How newsletter titles are formatted
  - Default: "{name} - Week {week}"
- Footer Text: Text that appears at bottom of newsletters
  - Example: "Brought to you by ACME Corporation"
- Footer URL: Company website
  - Example: "https://www.acme.com"
- Footer URL Display: Text shown for the link
  - Example: "www.acme.com"

#### **Wizard Step 3: Initial Keywords (Optional)**
- **Option A:** Add keywords manually
  - Click "Add Keyword"
  - Enter keyword (e.g., "polyurethane")
  - Select category (e.g., "Materials")
  - Repeat for each keyword

- **Option B:** Import from Excel/CSV
  - Upload file with columns: Keyword, Category
  - System imports automatically

- **Option C:** Leave empty
  - Customer will add keywords later in their User App

#### **Wizard Step 4: Initial Feeds (Optional)**
- **Option A:** Add RSS feeds manually
  - Click "Add Feed"
  - Enter RSS URL
  - Click "Test Feed" to verify it works
  - Select category
  - Repeat for each feed

- **Option B:** Leave empty
  - Customer will add feeds later in their User App

#### **Wizard Step 5: Deployment Configuration**
- Streamlit App URL: System suggests based on customer ID
  - Example: "acme-newsletter.streamlit.app"
  - You can edit if needed
- Deployment Tier/Plan: Select subscription level
- GitHub Token Instructions: System shows instructions for customer to generate token
  - (This happens after deployment, so you can note it for later)

#### **Wizard Step 6: Review & Confirm**
- System shows preview of all configuration
- Review each section
- Check for errors (highlighted in red if any)
- Click "Create Customer Configuration" button

#### **Wizard Step 7: Post-Deployment**
- System shows:
  - ✅ Created config files in GitHub
  - ✅ Streamlit secrets template (copy this!)
  - ✅ Deployment checklist
  - ✅ Welcome email template (with app URL filled in)

**What System Does Automatically:**
1. Validates customer ID is unique
2. Creates folder structure in GitHub: `customers/{customer_id}/`
3. Creates `branding.json` file
4. Creates `keywords.json` (empty or with your initial data)
5. Creates `feeds.json` (empty or with your initial data)
6. Creates `customer_info.json` (contact/subscription info)
7. Commits all files to GitHub
8. Adds customer to admin customer list

---

### **Phase 3: Deploy Streamlit App**

**After config files are created, deploy the customer's User App:**

#### **Step 1: Go to Streamlit Cloud**
- Login to: https://share.streamlit.io
- Click "New app"

#### **Step 2: Configure App**
- **Repository:** Select your GitHub repo (`org/newsletter-tool`)
- **Branch:** Select main branch
- **Main file:** `streamlit_user_app.py`
- **App URL:** System suggests based on customer ID, or enter custom

#### **Step 3: Set Secrets**
- Click "Advanced settings" → "Secrets"
- Paste the secrets template from Step 7 of onboarding wizard:
  ```toml
  customer_id = "acme"
  github_token = "ghp_..."  # Customer needs to generate this
  github_repo = "org/newsletter-tool"
  ```
- Save secrets

**Note:** Customer needs to generate GitHub token first (instructions provided in wizard Step 7)

#### **Step 4: Deploy**
- Click "Deploy"
- Wait for deployment (1-2 minutes)
- System shows: "App is live!" with URL

#### **Step 5: Test Deployment**
- Open the app URL in browser
- Verify:
  - ✅ App loads
  - ✅ Shows correct company branding
  - ✅ Config loads from GitHub
  - ✅ Can find news articles
  - ✅ Can generate newsletter

---

### **Phase 4: Customer GitHub Token Setup**

**Customer needs to provide a GitHub token:**

1. **Send customer instructions** (from wizard Step 7):
   ```
   To access your newsletter app, you need a GitHub token:
   
   1. Go to: https://github.com/settings/tokens
   2. Click "Generate new token (classic)"
   3. Name: "Newsletter Tool Access"
   4. Expiration: 1 year (or your preference)
   5. Select scopes: "repo" (full control)
   6. Click "Generate token"
   7. Copy the token immediately (you won't see it again!)
   8. Send it to us securely
   ```

2. **Receive token from customer** (via secure channel)

3. **Update Streamlit secrets:**
   - Go to Streamlit Cloud → Your app → Settings → Secrets
   - Update `github_token` with customer's token
   - App restarts automatically

---

### **Phase 5: Provide Customer Access**

#### **Step 1: Update Customer Record**
- In Admin Dashboard → Customer Management
- Find customer → Edit
- Update:
  - Status: "Active"
  - Streamlit App URL: `https://acme-newsletter.streamlit.app`
  - Deployment Date: Today's date

#### **Step 2: Send Welcome Email**
- Use template from wizard Step 7
- Customize with:
  - Customer's name
  - App URL: `https://acme-newsletter.streamlit.app`
  - Quick start guide
  - Support contact info

**Welcome Email Template:**
```
Subject: Welcome to Your Newsletter Tool!

Dear [Customer Name],

Your personalized Newsletter Tool is now ready!

Access your app here: https://acme-newsletter.streamlit.app

Quick Start:
1. Click "Find News" to search for articles
2. Preview articles you're interested in
3. Select articles for your newsletter
4. Click "Generate Newsletter"
5. Download your newsletter (HTML format)

Need Help?
- Contact: support@yourcompany.com
- Phone: [support phone]

We're here to help!

Best regards,
[Your Name]
```

---

### **Phase 6: Post-Deployment Follow-Up**

**Within 24-48 hours:**
- Check if customer has accessed the app
- Monitor first newsletter generation
- Reach out if no activity

**First Week:**
- Check customer's keywords/feeds (did they add more?)
- Verify newsletters are being generated
- Address any questions or issues

---

## Information Gathering Checklist

**Use this checklist when talking to customers:**

### ✅ Company & Contact Info
- [ ] Company Name: ________________
- [ ] Short Name: ________________
- [ ] Contact Name: ________________
- [ ] Contact Email: ________________
- [ ] Phone: ________________

### ✅ Branding
- [ ] Application Name: ________________
- [ ] Newsletter Title Format: ________________
- [ ] Footer Text: ________________
- [ ] Website URL: ________________

### ✅ Keywords
- [ ] Keyword 1: ________________ → Category: ________________
- [ ] Keyword 2: ________________ → Category: ________________
- [ ] Keyword 3: ________________ → Category: ________________
- [ ] (Add more as needed)

### ✅ RSS Feeds (Optional)
- [ ] Feed 1: ________________ → Category: ________________
- [ ] Feed 2: ________________ → Category: ________________
- [ ] (Add more as needed)

### ✅ Subscription
- [ ] Tier: ________________
- [ ] Start Date: ________________
- [ ] Renewal Date: ________________

---

## Common Scenarios

### **Scenario 1: Customer Doesn't Know Their Keywords Yet**
**Solution:** 
- Leave keywords empty in Step 3
- Customer can add them later in their User App
- They'll learn what works best by using the app

### **Scenario 2: Customer Has Many Keywords (50+)**
**Solution:**
- Ask them to provide Excel/CSV file
- Import in Step 3 using "Import from Excel" feature
- Faster than manual entry

### **Scenario 3: Customer Wants to See Examples First**
**Solution:**
- Set up with minimal config (just branding + 1-2 keywords)
- Deploy the app
- Customer can explore and add more keywords/feeds themselves
- Much easier for them to see what works

### **Scenario 4: Customer Needs Custom Branding**
**Solution:**
- In Step 2, customize all branding fields
- Preview in Step 6 before creating
- Can always edit later via Admin Dashboard if needed

---

## Time Estimate

- **Information Gathering:** 15-30 minutes (conversation or form)
- **Entering into Admin Dashboard:** 10-15 minutes (if all info ready)
- **Streamlit Deployment:** 5-10 minutes
- **Testing & Verification:** 5 minutes
- **Customer Token Setup:** 5 minutes (customer does this)
- **Welcome Email & Follow-up:** 5 minutes

**Total Time:** ~45-65 minutes per customer

---

## Tips for Efficient Onboarding

1. **Prepare in Advance:**
   - Have onboarding checklist ready
   - Know default values for optional fields
   - Have example keywords/feeds ready to suggest

2. **Customer Education:**
   - Explain that keywords/feeds can be changed later
   - Emphasize they'll learn what works by using the app
   - Don't worry about getting everything perfect upfront

3. **Batch Processing:**
   - If onboarding multiple customers, collect all info first
   - Then enter them all into admin dashboard in one session

4. **Use Templates:**
   - Save common keyword categories
   - Reuse for similar industry customers
   - Create onboarding email templates

---

## Troubleshooting

**Problem:** Customer ID already exists
- **Solution:** Try adding number (e.g., "acme2") or different identifier

**Problem:** RSS feed test fails
- **Solution:** Check URL format, verify feed is publicly accessible

**Problem:** Streamlit deployment fails
- **Solution:** Check GitHub token has correct permissions, verify repo path

**Problem:** Customer can't access app
- **Solution:** Verify Streamlit secrets are correct, check GitHub token validity

---

## Document Revision History

- **2025-01-XX:** Initial practical onboarding guide created

