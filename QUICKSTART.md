# Quick Start Guide

Get your Vinted Price Bot running in 5 minutes!

## Step 1: Clone and Install (2 minutes)

```bash
# Clone the repository
git clone <your-repo-url>
cd Vinted_price_tracker

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Google Sheets Setup (2 minutes)

### A. Create Service Account
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project
3. Enable **Google Sheets API** and **Google Drive API**
4. Create Service Account (APIs & Services → Credentials)
5. Download JSON key as `service_account.json`

### B. Create Google Sheet
1. Create a new Google Sheet
2. Copy the Sheet ID from URL: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
3. Open `service_account.json` and find `client_email`
4. Share your sheet with that email (Editor access)

## Step 3: Configure Bot (1 minute)

Run the setup wizard:
```bash
python setup.py
```

Or manually create `.env`:
```env
VINTED_EMAIL=your_email@example.com
VINTED_PASSWORD=your_password
VINTED_PROFILE_URL=https://www.vinted.lv/member/YOUR_ID
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=./service_account.json
DEFAULT_PRICE_CHANGE_PERCENT=10
```

## Step 4: Test & Populate (2 minutes)

```bash
# Test connections
python test_connection.py

# Fetch your items and populate Google Sheets
python fetch_items.py

# Review your Google Sheet - customize price changes!

# (Optional) Test price updates locally
python vinted_price_bot.py
```

## Step 5: Deploy to GitHub Actions

1. Push code to GitHub
2. Go to Settings → Secrets → Actions
3. Add these secrets:
   - `VINTED_EMAIL`
   - `VINTED_PASSWORD`
   - `VINTED_PROFILE_URL`
   - `GOOGLE_SHEET_ID`
   - `GOOGLE_SERVICE_ACCOUNT_JSON` (paste entire JSON content)
   
4. Done! Bot runs every Sunday at 10 AM UTC

## How to Use

1. Bot fetches your Vinted items
2. Saves them to Google Sheets
3. Edit "Price Change %" column in the sheet:
   - `10` = increase by 10%
   - `-5` = decrease by 5%
   - blank = use default (10%)
4. Bot updates prices automatically

## Troubleshooting

**Login fails?**
- Check credentials in `.env`
- Vinted might block automation (use with caution)

**Google Sheets error?**
- Verify sheet is shared with service account
- Check if APIs are enabled

**Items not found?**
- Verify profile URL is correct
- Check if you have items listed

## Need Help?

See full [README.md](README.md) for detailed instructions and troubleshooting.

