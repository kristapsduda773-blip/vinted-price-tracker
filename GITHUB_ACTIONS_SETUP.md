# GitHub Actions Setup - Complete Guide

This guide will help you deploy the Vinted Price Tracker Bot to run automatically every week via GitHub Actions.

## Prerequisites

Before starting, make sure you have:
- ✅ GitHub account
- ✅ Your `.env` file configured locally
- ✅ `service_account.json` file
- ✅ Bot tested locally (`python fetch_items.py` works)
- ✅ Google Sheet shared with service account

## Step-by-Step Setup

### Step 1: Create GitHub Repository

1. **Go to GitHub**: https://github.com/new
2. **Repository name**: `vinted-price-tracker`
3. **Description**: "Automated Vinted price tracker with Google Sheets"
4. **Visibility**: Choose **Private** (recommended) or Public
5. **Important**: ❌ **Do NOT** check these boxes:
   - ❌ Add a README file
   - ❌ Add .gitignore
   - ❌ Choose a license
   
   (We already have these files!)

6. **Click**: "Create repository"

### Step 2: Push Your Code to GitHub

Open terminal in your project folder and run:

```bash
# If you haven't already initialized git
git init
git add .
git commit -m "Initial commit: Vinted Price Tracker Bot"
git branch -M main

# Add your repository (replace with your username)
git remote add origin https://github.com/YOUR-USERNAME/vinted-price-tracker.git

# Push to GitHub
git push -u origin main
```

**Replace `YOUR-USERNAME`** with your actual GitHub username!

### Step 3: Add GitHub Secrets

This is the most important step! GitHub Secrets keep your credentials safe.

#### 3.1 Navigate to Secrets

1. Go to your repository on GitHub
2. Click **Settings** tab (top menu)
3. In left sidebar: **Secrets and variables** → **Actions**
4. You'll see "Actions secrets and variables"

#### 3.2 Add Each Secret

Click **"New repository secret"** button for each of these:

---

#### Secret #1: VINTED_EMAIL

- **Name**: `VINTED_EMAIL` (exactly like this)
- **Value**: Your Vinted account email
- **Example**: `john.doe@gmail.com`

Click "Add secret"

---

#### Secret #2: VINTED_PASSWORD

- **Name**: `VINTED_PASSWORD`
- **Value**: Your Vinted account password
- **Example**: `MySecurePassword123`

Click "Add secret"

---

#### Secret #3: VINTED_PROFILE_URL

- **Name**: `VINTED_PROFILE_URL`
- **Value**: `https://www.vinted.lv/member/295252411`

Click "Add secret"

---

#### Secret #4: GOOGLE_SHEET_ID

- **Name**: `GOOGLE_SHEET_ID`
- **Value**: `1PO8zzalK5Fvfjub3HyB5E0bKcnMxvPbDSH_XpSgd7RU`

Click "Add secret"

---

#### Secret #5: GOOGLE_SERVICE_ACCOUNT_JSON ⚠️ IMPORTANT!

This is the trickiest one - you need to paste the **ENTIRE** content of your `service_account.json` file.

1. **Open** `service_account.json` in a text editor (Notepad, VS Code, etc.)
2. **Select ALL** content (Ctrl+A / Cmd+A)
3. **Copy** (Ctrl+C / Cmd+C)

4. In GitHub:
   - **Name**: `GOOGLE_SERVICE_ACCOUNT_JSON`
   - **Value**: Paste the ENTIRE JSON content

Your JSON should look like this (this is just an example):
```json
{
  "type": "service_account",
  "project_id": "your-project-12345",
  "private_key_id": "abc123def456...",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhki...\n-----END PRIVATE KEY-----\n",
  "client_email": "vinted-bot@your-project.iam.gserviceaccount.com",
  "client_id": "1234567890",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/..."
}
```

Make sure you paste **ALL** of it, including the opening `{` and closing `}`!

Click "Add secret"

---

#### Secret #6: DEFAULT_PRICE_CHANGE_PERCENT (Optional)

- **Name**: `DEFAULT_PRICE_CHANGE_PERCENT`
- **Value**: `10`

This is optional. If you don't add it, the default is 10%.

Click "Add secret"

---

### Step 4: Verify All Secrets Are Added

After adding all secrets, you should see this list:

```
Repository secrets
- VINTED_EMAIL
- VINTED_PASSWORD
- VINTED_PROFILE_URL
- GOOGLE_SHEET_ID
- GOOGLE_SERVICE_ACCOUNT_JSON
- DEFAULT_PRICE_CHANGE_PERCENT (optional)
```

**Important**: You won't be able to see the secret values after saving them. This is normal for security!

### Step 5: Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If you see a message about workflows, click **"I understand my workflows, go ahead and enable them"**
3. You should see the workflow: **"Vinted Price Update"**

### Step 6: Test the Workflow (Manual Run)

Before waiting for the weekly schedule, let's test it manually:

1. Click **Actions** tab
2. In left sidebar, click **"Vinted Price Update"**
3. You'll see a blue button **"Run workflow"** (right side)
4. Click **"Run workflow"** dropdown
5. Leave branch as "main"
6. Click green **"Run workflow"** button

### Step 7: Watch It Run

1. After clicking "Run workflow", wait a few seconds and refresh
2. You'll see a new workflow run appear (yellow dot = running)
3. Click on it to see details
4. Click on **"update-prices"** job to see live logs

**What you'll see:**
```
Run python vinted_price_bot.py
==========================================
Starting Vinted Price Bot
==========================================
Setting up Chrome WebDriver...
Logging into Vinted...
Successfully logged into Vinted
Fetching items...
Found 25 items
...
Bot completed! Updated 20/25 items
==========================================
```

### Step 8: Check Results

**If successful (green checkmark ✅):**
1. Open your Google Sheet: https://docs.google.com/spreadsheets/d/1PO8zzalK5Fvfjub3HyB5E0bKcnMxvPbDSH_XpSgd7RU
2. Check "Last Updated" column - should show recent timestamp
3. Go to Vinted and verify prices changed
4. Check "Current Price" and "New Price" columns match

**If failed (red X ❌):**
- Click on the failed run
- Read the error message
- See "Troubleshooting" section below

## Automatic Schedule

Once set up, the bot runs automatically:

**Default**: Every **Sunday at 10:00 AM UTC**

### What Time is That for You?

- **GMT/London**: 10:00 AM
- **CET (Latvia/Germany)**: 11:00 AM
- **EST (New York)**: 5:00 AM
- **PST (LA)**: 2:00 AM

### Change the Schedule

Edit `.github/workflows/vinted_price_update.yml`:

```yaml
schedule:
  - cron: '0 10 * * 0'  # Every Sunday at 10 AM UTC
```

**Cron format**: `minute hour day-of-month month day-of-week`

**Examples**:
```yaml
# Every Monday at 9 AM UTC
- cron: '0 9 * * 1'

# Every day at 8 AM UTC
- cron: '0 8 * * *'

# Every Wednesday and Saturday at 10 AM UTC
- cron: '0 10 * * 3,6'

# First day of every month at 12 PM UTC
- cron: '0 12 1 * *'

# Every 6 hours
- cron: '0 */6 * * *'
```

After changing, commit and push:
```bash
git add .github/workflows/vinted_price_update.yml
git commit -m "Update schedule"
git push
```

## Workflow Details

Your workflow does this automatically:

1. ✅ Checks out your code
2. ✅ Sets up Python 3.11
3. ✅ Installs dependencies
4. ✅ Installs Chrome browser
5. ✅ Creates .env from secrets
6. ✅ Creates service_account.json from secret
7. ✅ Runs the bot
8. ✅ Uploads logs (kept for 30 days)

## View Logs

**To see what happened in a run:**

1. Go to **Actions** tab
2. Click on a workflow run
3. Click **"update-prices"** job
4. Expand each step to see output

**To download logs:**

1. Go to workflow run
2. Scroll to bottom "Artifacts"
3. Click **"bot-logs"** to download
4. Extract and open `vinted_bot.log`

## Troubleshooting

### ❌ Error: "Repository not found"

**Problem**: Git push fails

**Solution**:
```bash
# Check remote URL
git remote -v

# Update with correct username
git remote set-url origin https://github.com/YOUR-USERNAME/vinted-price-tracker.git

# Try push again
git push -u origin main
```

### ❌ Error: "Authentication failed"

**Problem**: GitHub requires authentication

**Solution 1 - Personal Access Token**:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Check "repo" scope
4. Copy the token
5. When pushing, use token as password

**Solution 2 - GitHub CLI**:
```bash
gh auth login
git push -u origin main
```

### ❌ Workflow Error: "Invalid JSON"

**Problem**: GOOGLE_SERVICE_ACCOUNT_JSON is not valid

**Solution**:
1. Open `service_account.json` locally
2. Verify it's valid JSON (use https://jsonlint.com/)
3. Copy **ALL** content (including { and })
4. Re-add the secret in GitHub

### ❌ Workflow Error: "Google Sheets authentication failed"

**Problem**: Sheet not shared or wrong credentials

**Solution**:
1. Open `service_account.json`
2. Copy the `client_email` value
3. Go to your Google Sheet
4. Click Share
5. Add that email as Editor
6. Make sure "Notify people" is UNCHECKED
7. Save

### ❌ Workflow Error: "Vinted login failed"

**Problem**: Wrong credentials or Vinted blocking

**Solutions**:
1. Verify VINTED_EMAIL secret is correct
2. Verify VINTED_PASSWORD secret is correct
3. Try logging in manually on Vinted to confirm credentials work
4. Check if Vinted requires 2FA (might need app password)

### ❌ Workflow Error: "No items found"

**Problem**: Profile URL wrong or items not public

**Solutions**:
1. Verify VINTED_PROFILE_URL is correct
2. Make sure you have items listed
3. Check items are public/active
4. Try accessing URL in incognito browser

## Security Best Practices

### ✅ DO:
- Use Private repository if possible
- Use strong, unique passwords
- Regularly review workflow runs
- Rotate credentials every few months
- Use a dedicated Vinted account for automation

### ❌ DON'T:
- Never commit `.env` to GitHub (it's in .gitignore)
- Never commit `service_account.json` (it's in .gitignore)
- Never share your secrets with anyone
- Never use your main Vinted account
- Don't log sensitive data

## Disabling the Bot

### Temporarily (Vacation Mode)

**Option 1**: Disable workflow
1. Actions → Vinted Price Update
2. Click "..." (top right)
3. Click "Disable workflow"

**Option 2**: Set all prices to 0%
1. Open Google Sheet
2. Set all "Price Change %" to `0`
3. Bot runs but makes no changes

### Permanently

Delete the workflow file:
```bash
rm .github/workflows/vinted_price_update.yml
git add .
git commit -m "Disable automatic price updates"
git push
```

## Monitoring

### Check if Bot is Working

**Every week, verify**:
1. Go to Actions tab
2. Check latest run has green ✓
3. Open Google Sheet
4. Verify "Last Updated" is recent
5. Spot-check a few items on Vinted

### Set Up Notifications (Optional)

GitHub can email you when workflows fail:

1. GitHub → Settings (your account settings, not repo)
2. Notifications → Actions
3. Enable "Send notifications for failed workflows"

## FAQ

**Q: How much does GitHub Actions cost?**
A: Free! GitHub Actions includes 2,000 free minutes/month for private repos. This bot uses ~5 minutes per run, so you can run it 400 times/month free.

**Q: Can I run it more frequently?**
A: Yes, but be careful not to spam Vinted. Weekly is recommended. Daily is probably okay. Hourly is excessive.

**Q: Can I run it for multiple profiles?**
A: Not currently. You'd need to modify the code. Each profile would need its own sheet.

**Q: What if Vinted updates their website?**
A: The bot might break. You'll need to update CSS selectors in the code. Check GitHub Issues for updates.

**Q: Is this against Vinted's terms of service?**
A: Possibly. Vinted doesn't have an official API. Use at your own risk. Your account could be suspended.

**Q: Can I use this for other countries?**
A: Yes, but you might need to adjust the URLs and selectors. Currently optimized for Vinted Latvia (.lv).

## Next Steps

After successful setup:

1. ✅ Monitor first few runs
2. ✅ Adjust price percentages in Google Sheet
3. ✅ Review pricing strategy weekly
4. ✅ Track which items sell
5. ✅ Optimize percentages based on results

## Support

**Still stuck?**

1. Check workflow logs for error messages
2. Review all secrets are correct
3. Verify Google Sheet is shared
4. Try running locally: `python vinted_price_bot.py`
5. See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
6. Open GitHub Issue with:
   - Error message (remove sensitive data)
   - Steps you've tried
   - Workflow run link

---

**Congratulations!** 🎉 Your bot is now automated and will run every week!

Last updated: 2026-01-18

