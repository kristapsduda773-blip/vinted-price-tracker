# Vinted Price Tracker Bot

Automatically update your Vinted item prices based on percentage changes defined in Google Sheets. The bot runs weekly via GitHub Actions.

## Features

- 🔄 Automatically scrapes your Vinted listed items
- 📊 Syncs item data with Google Sheets
- 💰 Updates prices based on customizable percentages
- ✅ Bulk price updates (dry-run by default, `--apply` to execute)
- 🆕 Detects new items automatically (adds them to sheet)
- 🗑️ Detects sold/removed items (marks them as removed)
- ⏰ Runs weekly via GitHub Actions
- 📝 Detailed logging of all operations
- 🔒 Secure credential management via GitHub Secrets

## How It Works

1. **Initial Setup**: Run `fetch_items.py` to populate Google Sheets with all your items
2. **Customize**: Edit the "Price Change %" column in the sheet for each item
3. **Automatic Updates**: Bot runs weekly to:
   - Re-fetch current prices from Vinted
   - **Detect new items** (automatically adds them with default %)
   - **Detect removed items** (marks them as "❌ Sold/Removed")
   - Read your custom percentages from Google Sheets
   - Calculate new prices based on percentages
   - Update prices on Vinted automatically
4. Runs every Sunday at 10:00 AM UTC (customizable)

## Setup Instructions

### 1. Google Sheets Setup

#### Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable **Google Sheets API** and **Google Drive API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API" and enable it
   - Search for "Google Drive API" and enable it

#### Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in service account details and click "Create"
4. Grant it "Editor" role (or "Owner" for full access)
5. Click "Done"

#### Generate Service Account Key

1. Click on the created service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose JSON format
5. Download the JSON file (this is your `service_account.json`)

#### Create Google Sheet

1. Create a new Google Sheet
2. Copy the Sheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit`
3. Share the sheet with the service account email:
   - Open the JSON file and find the `client_email` field
   - Share your Google Sheet with this email address (Editor access)

The bot will automatically create the following columns:
- **Item ID**: Vinted item identifier
- **Title**: Item name
- **Current Price**: Current price on Vinted
- **New Price**: Calculated new price
- **Price Change %**: Percentage to change price (you can edit this!)
- **Status**: Item status (Active or ❌ Sold/Removed)
- **Last Updated**: Timestamp of last update

**To customize price changes**: Simply edit the "Price Change %" column for any item. Leave blank for default (10%).

**New items**: Automatically added with default % when detected  
**Sold items**: Automatically marked as "❌ Sold/Removed" (kept for records)

### 2. GitHub Repository Setup

1. Fork or create a new repository with this code
2. Go to repository **Settings** > **Secrets and variables** > **Actions**
3. Add the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `VINTED_EMAIL` | Your Vinted account email | `your-email@example.com` |
| `VINTED_PASSWORD` | Your Vinted account password | `your-password` |
| `VINTED_PROFILE_URL` | Your Vinted profile URL | `https://www.vinted.lv/member/295252411` |
| `GOOGLE_SHEET_ID` | Your Google Sheet ID | `1BxiM...VtWE` |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | **Entire content** of service_account.json file | `{"type": "service_account", ...}` |
| `DEFAULT_PRICE_CHANGE_PERCENT` | Default % change (optional) | `10` |

### 3. Running the Bot

#### Automatic (GitHub Actions)

The bot runs automatically every Sunday at 10:00 AM UTC. You can also trigger it manually:

1. Go to **Actions** tab in your repository
2. Select "Vinted Price Update" workflow
3. Click "Run workflow"

#### Local Testing

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Vinted_price_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Edit `.env` with your credentials:
```env
VINTED_EMAIL=your_email@example.com
VINTED_PASSWORD=your_password
VINTED_PROFILE_URL=https://www.vinted.lv/member/295252411
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=./service_account.json
DEFAULT_PRICE_CHANGE_PERCENT=10
```

5. Place your `service_account.json` in the project root

6. **Fetch your items and populate Google Sheets:**
```bash
python fetch_items.py
```

This will:
- Scrape all your listed Vinted items
- Populate Google Sheets with item details
- Set default price change % (10%)

7. **Review and customize** your Google Sheet:
- Open the sheet and review your items
- Edit "Price Change %" column for each item
- Positive numbers increase (e.g., 10 = +10%)
- Negative numbers decrease (e.g., -15 = -15%)

8. **Run price updates** (optional - test locally first):
```bash
python vinted_price_bot.py            # dry-run (no Vinted edits)
python vinted_price_bot.py --apply    # actually updates prices on Vinted
```

### Bulk editing (how to do it in practice)

Vinted doesn’t reliably expose a “bulk edit prices” button for regular sellers, so brands typically do this with **automation**:
- pull all active listings,
- compute a new price per listing (usually with a % rule + rounding/floor),
- then update each listing programmatically (with pacing and safety limits).

This repo follows that same pattern, but uses Google Sheets as the control panel.

#### The fast way: change many items at once in Google Sheets

- Select the entire **“Price Change %”** column range and mass-fill it (type a value once, then drag the fill handle down).
- Or use formulas (example): set all active rows to `-10` to reduce by 10%.

Then run the bot. By default it’s a **dry-run**; add `--apply` when you’re ready.

#### Useful run options

```bash
# Preview what would change (no Vinted edits)
python vinted_price_bot.py

# Manual workflow: generate a clickable worklist (recommended if Vinted blocks automation)
python vinted_price_bot.py --manual --export-html manual_price_updates.html --open-html

# Apply changes to the first 25 matching items
python vinted_price_bot.py --apply --limit 25

# Only apply to specific item IDs
python vinted_price_bot.py --apply --only-ids 123456789,987654321

# Only apply to items whose title contains a keyword
python vinted_price_bot.py --apply --title-contains "nike"
```

### Recommended if you get blocked: manual update worklist

If Vinted blocks automated edits, use the bot only to:
- scrape + sync your items to Google Sheets
- compute new prices
- generate an HTML page with **Edit** links + the **New Price** you should type

Run:

```bash
python vinted_price_bot.py --manual --export-html manual_price_updates.html --open-html
```

In the generated page, use **“Open next batch of Edit links”** to open tabs in small batches (e.g. 10).

⚠️ Note: automating Vinted may violate their Terms and can trigger captchas/blocks. Use conservative limits and delays.

## Configuration

### Change Schedule

Edit `.github/workflows/vinted_price_update.yml`:

```yaml
schedule:
  - cron: '0 10 * * 0'  # Every Sunday at 10:00 AM UTC
```

Cron format: `minute hour day month weekday`

Examples:
- `0 10 * * 0` - Every Sunday at 10:00 AM
- `0 10 * * 1` - Every Monday at 10:00 AM
- `0 10 * * *` - Every day at 10:00 AM
- `0 10 1 * *` - First day of every month at 10:00 AM

### Price Change Examples

In Google Sheets, set the "Price Change %" column:

- `10` - Increase price by 10%
- `-10` - Decrease price by 10%
- `20` - Increase price by 20%
- `0` - Keep price the same
- *(blank)* - Use default (10%)

**Example:**
- Current price: €50
- Price Change %: 20
- New price: €60 (50 * 1.20)

## Logs

- Logs are saved to `vinted_bot.log`
- GitHub Actions logs are available in the Actions tab
- Log artifacts are retained for 30 days

## Troubleshooting

### Bot fails to login
- Check your Vinted credentials in GitHub Secrets
- Vinted may have changed their login flow - update selectors in code
- Try enabling 2FA and using app-specific password

### Items not found
- Verify your profile URL is correct
- Check if Vinted's HTML structure changed
- Try running locally with headless mode disabled to see what's happening

### Google Sheets authentication fails
- Verify service account JSON is correct
- Check if APIs are enabled (Sheets + Drive)
- Ensure sheet is shared with service account email

### Price updates fail
- Vinted may have changed their edit flow
- Check item edit page structure
- Rate limiting - add more delays between updates

## Security Notes

⚠️ **Important Security Practices:**

- Never commit `.env` or `service_account.json` to Git
- Use GitHub Secrets for all sensitive data
- Regularly rotate your passwords
- Review GitHub Actions logs for any leaked credentials
- Consider using a dedicated Vinted account for automation

## Legal Disclaimer

This bot automates interaction with Vinted's website. Use at your own risk:

- Vinted's Terms of Service may prohibit automated access
- Your account could be suspended or banned
- Web scraping may break if Vinted updates their site
- No warranties or guarantees are provided

**Use responsibly and at your own discretion.**

## Documentation

- **README.md** (this file) - Complete setup and usage guide
- **QUICKSTART.md** - Get started in 5 minutes
- **GITHUB_ACTIONS_SETUP.md** - Deploy to GitHub Actions
- **USAGE_GUIDE.md** - Detailed usage examples and scenarios
- **QUICK_REFERENCE.md** - Quick commands cheat sheet

## Support

For issues or questions:
1. Check the logs for error messages
2. Review the troubleshooting section
3. Run `python test_connection.py` to diagnose
4. See GITHUB_ACTIONS_SETUP.md for deployment help
5. Open an issue on GitHub with:
   - Error message
   - Log excerpt (remove sensitive data)
   - Steps to reproduce

## License

MIT License - feel free to modify and distribute.

---

**Made with ❤️ for Vinted sellers**

