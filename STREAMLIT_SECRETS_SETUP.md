# Streamlit Secrets Setup Guide

## Required Secrets for gnpuser (GlobalNewsPilot)

Your Streamlit app needs GitHub API credentials to access the repository.

### Steps to Add Secrets:

1. **Go to Streamlit Cloud Dashboard**
   - Visit: https://share.streamlit.io
   - Navigate to your app: `gnpuser`
   - Click on "⚙️ Settings" (or "Settings" in the app menu)
   - Click on "Secrets" tab

2. **Add the following secrets:**

```toml
github_token = "your_github_personal_access_token_here"
github_repo = "stefanhermes-code/newsletter"
```

### How to Get GitHub Token:

1. **Go to GitHub.com**
   - Click your profile picture (top right)
   - Go to "Settings"
   - Scroll down to "Developer settings" (bottom left)
   - Click "Personal access tokens" → "Tokens (classic)"
   - Click "Generate new token" → "Generate new token (classic)"

2. **Configure Token:**
   - **Note**: "GlobalNewsPilot App"
   - **Expiration**: Choose your preferred expiration (90 days, 1 year, or no expiration)
   - **Scopes**: Check these permissions:
     - ✅ `repo` (Full control of private repositories)
       - This includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`, `security_events`

3. **Generate and Copy Token**
   - Click "Generate token"
   - **IMPORTANT**: Copy the token immediately (you won't be able to see it again!)
   - Paste it into Streamlit secrets as `github_token`

### Complete Secrets Configuration:

**For User App (gnpuser):**
```toml
github_token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
github_repo = "stefanhermes-code/newsletter"
```

**For Admin App (gnp-backend):**
```toml
github_token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
github_repo = "stefanhermes-code/newsletter"
admin_username = "admin"
admin_password = "your_secure_admin_password_here"
```

**Note:** Set a strong password for `admin_password` in the Admin App secrets!

### After Adding Secrets:

1. Save the secrets
2. Streamlit Cloud will automatically restart your app
3. The app should now be able to connect to GitHub

### Testing:

Once secrets are added, the app should be able to:
- ✅ Load customer configurations
- ✅ Authenticate users (read `user_access.json`)
- ✅ Load keywords and RSS feeds
- ✅ Save newsletters to GitHub
- ✅ Save configuration changes

### Troubleshooting:

**Error: "Failed to connect to GitHub"**
- Check that `github_token` is correct and has `repo` permissions
- Check that `github_repo` is exactly `"stefanhermes-code/newsletter"` (no quotes in the value)
- Verify token hasn't expired

**Error: "github_token not found in Streamlit secrets"**
- Make sure secrets are saved in Streamlit Cloud
- Check spelling: `github_token` (not `githubToken` or `GITHUB_TOKEN`)

**Error: "Repository not found"**
- Check that `github_repo` is correct: `"stefanhermes-code/newsletter"`
- Verify the repository exists and is accessible with your token

