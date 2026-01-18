# GitHub Secrets Setup Guide

Follow these steps to configure GitHub Actions for your Vinted Price Bot.

## Step-by-Step Instructions

### 1. Navigate to Repository Settings

1. Go to your GitHub repository
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**

### 2. Add Repository Secrets

Click **New repository secret** for each of the following:

---

#### Secret 1: VINTED_EMAIL

- **Name:** `VINTED_EMAIL`
- **Value:** Your Vinted account email
- **Example:** `john.doe@example.com`

---

#### Secret 2: VINTED_PASSWORD

- **Name:** `VINTED_PASSWORD`
- **Value:** Your Vinted account password
- **Example:** `MySecurePassword123`

⚠️ **Security Note:** Consider creating a dedicated Vinted account for automation

---

#### Secret 3: VINTED_PROFILE_URL

- **Name:** `VINTED_PROFILE_URL`
- **Value:** Your Vinted profile URL
- **Example:** `https://www.vinted.lv/member/295252411`

**How to find your profile URL:**
1. Login to Vinted
2. Click your profile picture
3. Copy the URL from browser address bar

---

#### Secret 4: GOOGLE_SHEET_ID

- **Name:** `GOOGLE_SHEET_ID`
- **Value:** Your Google Sheet ID
- **Example:** `1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms`

**How to find Sheet ID:**
1. Open your Google Sheet
2. Look at the URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
3. Copy the `SHEET_ID` part

---

#### Secret 5: GOOGLE_SERVICE_ACCOUNT_JSON

- **Name:** `GOOGLE_SERVICE_ACCOUNT_JSON`
- **Value:** **Complete contents** of your `service_account.json` file

**Important:** Copy the ENTIRE JSON file content, including all braces `{}`.

**Example format:**
```json
{
  "type": "service_account",
  "project_id": "your-project-12345",
  "private_key_id": "abc123...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...",
  "client_email": "vinted-bot@your-project.iam.gserviceaccount.com",
  "client_id": "123456789",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/..."
}
```

**Steps:**
1. Open `service_account.json` in a text editor
2. Press Ctrl+A (or Cmd+A on Mac) to select all
3. Copy (Ctrl+C / Cmd+C)
4. Paste into the secret value field

---

#### Secret 6: DEFAULT_PRICE_CHANGE_PERCENT (Optional)

- **Name:** `DEFAULT_PRICE_CHANGE_PERCENT`
- **Value:** Default percentage for price changes
- **Example:** `10`

If not set, defaults to 10%.

---

## 3. Verify Secrets

After adding all secrets, you should see:

- ✅ VINTED_EMAIL
- ✅ VINTED_PASSWORD
- ✅ VINTED_PROFILE_URL
- ✅ GOOGLE_SHEET_ID
- ✅ GOOGLE_SERVICE_ACCOUNT_JSON
- ✅ DEFAULT_PRICE_CHANGE_PERCENT (optional)

## 4. Enable GitHub Actions

1. Go to **Actions** tab in your repository
2. If prompted, click **Enable GitHub Actions**
3. You should see "Vinted Price Update" workflow

## 5. Test the Workflow

### Manual Test Run

1. Go to **Actions** tab
2. Click **Vinted Price Update** workflow
3. Click **Run workflow** dropdown
4. Click **Run workflow** button
5. Watch the workflow run in real-time

### Check Results

- ✅ Green checkmark = Success!
- ❌ Red X = Failed (click to see logs)

## 6. Schedule

The bot runs automatically every Sunday at 10:00 AM UTC.

**To change schedule:**
1. Edit `.github/workflows/vinted_price_update.yml`
2. Modify the cron expression:
```yaml
schedule:
  - cron: '0 10 * * 0'  # minute hour day month weekday
```

**Examples:**
- `0 10 * * 0` - Every Sunday 10 AM
- `0 10 * * 1` - Every Monday 10 AM
- `0 10 * * *` - Every day 10 AM
- `0 10 1 * *` - First day of month 10 AM
- `0 */6 * * *` - Every 6 hours

## Troubleshooting

### Workflow fails immediately
- Check that all secrets are added correctly
- Verify no extra spaces in secret values
- Make sure `GOOGLE_SERVICE_ACCOUNT_JSON` contains valid JSON

### Authentication errors
- Double-check VINTED_EMAIL and VINTED_PASSWORD
- Try logging in manually to verify credentials work
- Check if Vinted requires 2FA (may need app password)

### Google Sheets errors
- Verify sheet is shared with service account email
- Check Google Sheets API is enabled
- Verify GOOGLE_SHEET_ID is correct

### Need to view logs?
1. Go to Actions tab
2. Click on the failed workflow run
3. Click on "update-prices" job
4. Expand steps to see detailed logs
5. Download log artifacts if needed

## Security Best Practices

✅ **DO:**
- Use strong, unique passwords
- Regularly rotate credentials
- Review workflow logs for issues
- Delete old log artifacts

❌ **DON'T:**
- Share your secrets with anyone
- Commit secrets to Git
- Use your main Vinted account (create a separate one)
- Leave secrets in public repositories

## Need Help?

- Check workflow logs for error messages
- Review [README.md](README.md) troubleshooting section
- Open an issue on GitHub with:
  - Error message (remove sensitive data)
  - Steps to reproduce
  - Your configuration (without secrets)

---

**That's it! Your bot is now configured and will run automatically.** 🎉

