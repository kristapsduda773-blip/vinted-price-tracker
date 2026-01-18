# Google Sheets Template Guide

This guide explains the Google Sheets structure used by the Vinted Price Bot.

## Sheet Structure

The bot automatically creates and manages a Google Sheet with the following columns:

| Column | Description | Editable | Format |
|--------|-------------|----------|--------|
| **Item ID** | Unique Vinted item identifier | No | Numeric |
| **Title** | Item name/description | No | Text |
| **Current Price** | Current price on Vinted | No | Number (€) |
| **New Price** | Calculated price after % change | No | Number (€) |
| **Price Change %** | Percentage to change price | **YES** | Number |
| **Last Updated** | Timestamp of last sync | No | DateTime |

## Example Sheet

```
| Item ID  | Title               | Current Price | New Price | Price Change % | Last Updated        |
|----------|---------------------|---------------|-----------|----------------|---------------------|
| 12345678 | Nike Sneakers       | 50.00         | 55.00     | 10             | 2026-01-18 10:30:00 |
| 23456789 | Vintage T-Shirt     | 15.00         | 12.75     | -15            | 2026-01-18 10:30:00 |
| 34567890 | Designer Handbag    | 120.00        | 144.00    | 20             | 2026-01-18 10:30:00 |
| 45678901 | Winter Jacket       | 80.00         | 80.00     |                | 2026-01-18 10:30:00 |
```

## How to Use

### 1. First Run
- Bot fetches all your Vinted items
- Creates the sheet structure automatically
- Sets all items to default percentage (10%)

### 2. Customize Price Changes

Edit the **Price Change %** column for each item:

#### Examples:

**Increase Prices:**
- `10` = Increase by 10%
- `20` = Increase by 20%
- `5.5` = Increase by 5.5%

**Decrease Prices:**
- `-10` = Decrease by 10%
- `-20` = Decrease by 20%
- `-5` = Decrease by 5%

**No Change:**
- `0` = Keep current price
- Leave blank = Use default (10%)

### 3. Price Calculations

The bot calculates: **New Price = Current Price × (1 + Price Change % / 100)**

**Examples:**

| Current Price | Price Change % | Calculation | New Price |
|---------------|----------------|-------------|-----------|
| €50.00 | 10 | 50 × 1.10 | €55.00 |
| €50.00 | -10 | 50 × 0.90 | €45.00 |
| €50.00 | 20 | 50 × 1.20 | €60.00 |
| €50.00 | -25 | 50 × 0.75 | €37.50 |
| €50.00 | 0 | 50 × 1.00 | €50.00 |

### 4. Bot Updates

When the bot runs:
1. Fetches current prices from Vinted
2. Reads your custom percentages from sheet
3. Calculates new prices
4. Updates prices on Vinted
5. Updates sheet with new data

## Tips & Best Practices

### Dynamic Pricing Strategy

**Seasonal Adjustments:**
```
Winter Jacket:     +30%  (increase in fall/winter)
Summer Dress:      -20%  (decrease in winter)
```

**Demand-Based:**
```
Popular items:     +15%  (high demand)
Slow sellers:      -10%  (encourage sales)
```

**Time-Based:**
```
New listings:       0%   (keep original price)
Old listings:      -5%   (weekly decrease)
```

### Pricing Rules

✅ **Good Practices:**
- Start with small changes (5-10%)
- Monitor what sells and adjust
- Use negative percentages for slow items
- Keep designer items at 0% or small increases

❌ **Avoid:**
- Extreme changes (> 50%)
- Too frequent updates (weekly is good)
- Pricing below your costs
- Inconsistent pricing for similar items

### Bulk Operations

**Update multiple items:**
1. Select cells in Price Change % column
2. Type new percentage
3. Press Ctrl+D (or Cmd+D) to fill down

**Reset to default:**
1. Clear Price Change % column
2. Bot will use default (10%)

**Pause updates for specific items:**
- Set Price Change % to `0`
- Item keeps current price

## Advanced Usage

### Formula-Based Pricing

You can use Google Sheets formulas in the Price Change % column:

**Example: Automatic price reduction for old items**
```excel
=IF(DAYS(NOW(), F2) > 30, -10, 5)
```
This decreases price by 10% if item hasn't updated in 30 days, otherwise increases by 5%.

**Example: Price based on current price**
```excel
=IF(C2 < 20, 15, IF(C2 < 50, 10, 5))
```
This increases cheaper items more (15% if under €20, 10% if under €50, else 5%).

### Conditional Formatting

Make your sheet visual:

1. Select Price Change % column
2. Format → Conditional formatting
3. Add rules:
   - Green if > 0 (price increases)
   - Red if < 0 (price decreases)
   - Yellow if = 0 (no change)

### Data Tracking

**Add additional columns for your notes:**
- Cost basis
- Profit margin
- Category
- Season
- Status (active/sold)

The bot won't modify extra columns!

## Troubleshooting

### Sheet not updating?
- Check if sheet is shared with service account
- Verify GOOGLE_SHEET_ID in configuration
- Check bot logs for errors

### Prices not changing on Vinted?
- Bot might have failed to login
- Vinted might have blocked automation
- Check GitHub Actions logs

### Wrong calculations?
- Verify percentages are numbers (not text)
- Check for typos in Price Change % column
- Remember: negative numbers decrease price

## Sheet Permissions

**Service Account needs:**
- ✅ Editor access (to read and write)
- ✅ Sheet must be shared with service account email

**Your permissions:**
- ✅ Owner or Editor (to modify percentages)
- ✅ Can share with others as Viewer

## Example Scenarios

### Scenario 1: Clearance Sale
```
All items: -20% (clear inventory)
```

### Scenario 2: Seasonal Price Increase
```
Winter items: +25%
Summer items: -15%
All-season: 0%
```

### Scenario 3: Testing Optimal Price
```
Week 1: +10%
Week 2: +5% (if no sales from week 1)
Week 3: -5% (if still no sales)
Week 4: -10% (final reduction)
```

### Scenario 4: Premium Items
```
Designer bags: +20%
Vintage items: +15%
Regular clothes: +5%
Fast fashion: 0%
```

## Support

For issues with Google Sheets:
1. Check service account permissions
2. Verify sheet ID is correct
3. Review bot logs
4. See main [README.md](README.md) for troubleshooting

---

**Happy pricing!** 📊💰

