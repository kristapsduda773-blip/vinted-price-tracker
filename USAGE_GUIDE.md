# Usage Guide - Step by Step

This guide shows you exactly how to use the Vinted Price Tracker Bot after setup.

## Initial Setup - Populate Your Sheet

### Step 1: Fetch Your Items

Run the fetch script to get all your Vinted items into Google Sheets:

```bash
python fetch_items.py
```

**What it does:**
- Opens your Vinted profile (https://www.vinted.lv/member/295252411)
- Scrolls through all your listed items
- Extracts item details (ID, title, price, URL)
- Creates/updates Google Sheet with all items
- Sets default price change to 10% for all items

**Output Example:**
```
==========================================
Vinted Item Fetcher - Populating Google Sheets
==========================================
Setting up Chrome WebDriver...
Setting up Google Sheets connection...
Fetching items from your profile...
Scrolling to load all items...
Processing 25 items...
  [1] Nike Air Max Sneakers - €50.00 (ID: 12345678)
  [2] Vintage Band T-Shirt - €15.00 (ID: 23456789)
  [3] Designer Handbag - €120.00 (ID: 34567890)
  ...
Successfully extracted 25 unique items
Populating Google Sheets...
✅ Successfully populated sheet with 25 items
📊 Sheet URL: https://docs.google.com/spreadsheets/d/your-sheet-id
==========================================
✅ SUCCESS! 25 items added to Google Sheets
==========================================
```

### Step 2: Open Your Google Sheet

Your Google Sheet now looks like this:

| Item ID | Title | Current Price (€) | New Price (€) | Price Change % | URL | Last Updated |
|---------|-------|-------------------|---------------|----------------|-----|--------------|
| 12345678 | Nike Air Max Sneakers | 50.00 | 55.00 | 10 | https://... | 2026-01-18 10:30:00 |
| 23456789 | Vintage Band T-Shirt | 15.00 | 16.50 | 10 | https://... | 2026-01-18 10:30:00 |
| 34567890 | Designer Handbag | 120.00 | 132.00 | 10 | https://... | 2026-01-18 10:30:00 |

## Customize Your Pricing Strategy

### Step 3: Edit Price Change Percentages

Click on the "Price Change %" column and customize each item:

#### Example Strategies:

**Strategy 1: Clearance Sale**
```
All winter items:    -20%  (Reduce to clear old stock)
Summer items:        +10%  (Slight increase)
Popular brands:       +5%  (Small increase)
```

**Strategy 2: Test Market**
```
New listings:          0%  (Keep original price)
Week 2:              +10%  (Test higher price)
Week 3:               +5%  (Small increase if no sale)
Week 4:               -5%  (Reduce if still not sold)
```

**Strategy 3: Premium Pricing**
```
Designer items:      +20%  (Premium markup)
Vintage/rare:        +15%  (Collector's pricing)
Fast fashion:         +5%  (Standard markup)
```

**Strategy 4: Quick Sale**
```
Old listings:        -15%  (Encourage quick sale)
Damaged/used:        -25%  (Heavy discount)
New condition:        +5%  (Premium for quality)
```

### Example: Customize Your Sheet

Edit the "Price Change %" column:

| Item ID | Title | Current Price | New Price | **Price Change %** |
|---------|-------|---------------|-----------|-------------------|
| 12345678 | Nike Air Max Sneakers | 50.00 | 60.00 | **20** |
| 23456789 | Vintage Band T-Shirt | 15.00 | 12.75 | **-15** |
| 34567890 | Designer Handbag | 120.00 | 120.00 | **0** |
| 45678901 | Winter Jacket | 80.00 | 72.00 | **-10** |

**Tips:**
- ✅ Enter just the number (10, -15, 20)
- ✅ Positive = increase, Negative = decrease
- ✅ Leave blank = use default (10%)
- ✅ Use 0 = keep current price
- ❌ Don't use symbols (%, €)

## Update Prices

### Option 1: Automatic (GitHub Actions)

**Once deployed to GitHub:**

The bot runs automatically every Sunday at 10:00 AM UTC. It will:
1. Fetch current prices from Vinted
2. Read your percentages from Google Sheet
3. Calculate new prices
4. Update Vinted automatically
5. Update sheet with results

**Check if it worked:**
- Go to GitHub → Actions tab
- Click latest workflow run
- Green ✓ = Success
- Red ✗ = Check logs for errors

### Option 2: Manual (Local)

**Test price updates locally before deploying:**

```bash
python vinted_price_bot.py
```

**What happens:**
1. Logs into Vinted
2. Navigates to each item
3. Updates the price according to your percentages
4. Logs all changes

**Output Example:**
```
==========================================
Starting Vinted Price Bot
==========================================
Logging into Vinted...
Successfully logged into Vinted
Fetching items from profile...
Found 25 items
Syncing with Google Sheets...
Google Sheets updated with 25 items
Updating price for: Nike Air Max Sneakers
Price updated: €50.00 → €60.00 (+20.0%)
Updating price for: Vintage Band T-Shirt
Price updated: €15.00 → €12.75 (-15.0%)
Skipping Designer Handbag - no price change needed
...
==========================================
Bot completed! Updated 18/25 items
==========================================
```

### Option 3: Manual (GitHub Actions)

**Trigger the bot manually from GitHub:**

1. Go to your repository
2. Click **Actions** tab
3. Click **Vinted Price Update** workflow
4. Click **Run workflow** button
5. Click **Run workflow** (confirm)
6. Wait for completion (usually 2-5 minutes)

## Monitor & Adjust

### Review Results

After the bot runs, check your Google Sheet:

**What gets updated:**
- Current Price (€) - Latest price from Vinted
- New Price (€) - Calculated based on your %
- Last Updated - Timestamp of update

**What YOU control:**
- Price Change % - Edit anytime to change strategy

### Weekly Routine (Recommended)

**Every Monday morning (after Sunday bot run):**

1. Open Google Sheet
2. Review "Last Updated" column (should be yesterday)
3. Check which items sold (remove from sheet)
4. Adjust percentages based on performance:
   - Items not selling? Reduce price (-5% to -15%)
   - Items getting views? Increase price (+5% to +10%)
   - Just sold? Set to 0% to maintain new price
5. Save and close - bot will use new % next week

### Monthly Review

**Performance tracking:**

1. Track which strategies work best
2. Adjust default percentage if needed
3. Update `.env` with new `DEFAULT_PRICE_CHANGE_PERCENT`
4. Re-run `fetch_items.py` to refresh all items

## Common Scenarios

### Scenario 1: New Item Listed

**You listed a new item on Vinted**

1. Run `python fetch_items.py` to refresh
2. New item appears in sheet
3. Set custom percentage for new item
4. Wait for next bot run (or run manually)

### Scenario 2: Item Sold

**Item sold - you want to remove it**

1. Open Google Sheet
2. Delete the row for sold item
3. Bot will skip it next time
4. Or: Set Price Change % to blank (it will remain in sheet for records)

### Scenario 3: Change Pricing Strategy

**You want to try a new approach**

1. Open Google Sheet
2. Edit "Price Change %" column for multiple items:
   - Select cells
   - Enter new percentage
   - Press Ctrl+D (fill down) if same for all
3. Next bot run uses new percentages

### Scenario 4: Test One Item

**You want to test a new price on just one item**

1. Open Google Sheet
2. Find the item
3. Change its "Price Change %" (e.g., +50 for 50% increase)
4. Run bot: `python vinted_price_bot.py`
5. Check Vinted to see new price
6. If not happy, change % again and re-run

### Scenario 5: Pause All Updates

**You're on vacation - don't want any changes**

**Option A: Disable GitHub Actions**
1. Go to GitHub → Actions
2. Click "Vinted Price Update"
3. Click "..." → Disable workflow

**Option B: Set all to 0%**
1. Open Google Sheet
2. Select entire "Price Change %" column
3. Fill with 0
4. Bot will skip all updates

**Option C: Delete the workflow**
1. Temporarily remove `.github/workflows/vinted_price_update.yml`
2. Push to GitHub
3. No automatic runs until you add it back

## Advanced Tips

### Formula-Based Pricing

Use Google Sheets formulas in "Price Change %" column:

**Example 1: Time-based reduction**
```excel
=IF(DAYS(NOW(), G2) > 30, -10, 5)
```
If item older than 30 days: -10%, else +5%

**Example 2: Price-based strategy**
```excel
=IF(C2 < 20, 15, IF(C2 < 50, 10, 5))
```
Under €20: +15%, under €50: +10%, else +5%

**Example 3: Seasonal**
```excel
=IF(MONTH(NOW()) IN (11,12,1,2), 20, -10)
```
Winter months (Nov-Feb): +20%, else -10%

### Conditional Formatting

Make your sheet visual:

1. Select "Price Change %" column (E2:E999)
2. Format → Conditional formatting
3. Add rules:
   - **Green**: Value > 0 (price increases)
   - **Red**: Value < 0 (price decreases)  
   - **Yellow**: Value = 0 (no change)

### Track Performance

Add extra columns for your reference:

| ... | Price Change % | Cost Basis | Profit | Notes |
|-----|----------------|------------|--------|-------|
| ... | 10 | €30 | €25 | Popular item |
| ... | -15 | €20 | -€5 | Not selling |

The bot ignores extra columns - they're for you!

## Troubleshooting

### Items Not Appearing in Sheet

**Problem:** Ran `fetch_items.py` but sheet is empty

**Solutions:**
1. Check profile URL is correct in `.env`
2. Verify you have items listed on Vinted
3. Check logs: `fetch_items.log`
4. Vinted might have changed structure - check GitHub for updates

### Prices Not Updating on Vinted

**Problem:** Bot runs successfully but Vinted prices unchanged

**Solutions:**
1. Check if you're logged into Vinted
2. Verify items still exist (not sold/deleted)
3. Check bot logs for specific errors
4. Vinted might block automation - use with caution

### Sheet Not Syncing

**Problem:** Changes to percentages not reflected

**Solutions:**
1. Make sure you saved the sheet (Ctrl+S)
2. Wait for next bot run (weekly schedule)
3. Or run manually: `python vinted_price_bot.py`
4. Check Google Sheets API quota

## Getting Help

1. **Check logs:**
   - `fetch_items.log` - Fetching issues
   - `vinted_bot.log` - Bot operation issues

2. **Run tests:**
   ```bash
   python test_connection.py
   ```

3. **Review documentation:**
   - README.md - Full setup
   - GOOGLE_SHEETS_TEMPLATE.md - Sheet usage
   - GITHUB_SECRETS_SETUP.md - Deployment

4. **GitHub Issues:**
   - Open issue with error message
   - Include relevant log excerpts (remove sensitive data)

---

**Happy pricing! 💰**

For more help, see the [README.md](README.md) or open a GitHub issue.

