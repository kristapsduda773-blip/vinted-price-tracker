# Quick Reference Card

## 🚀 Quick Commands

### First Time Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (interactive)
python setup.py

# 3. Test everything
python test_connection.py

# 4. Fetch your items → Google Sheets
python fetch_items.py
```

### Regular Use
```bash
# Refresh items in Google Sheets
python fetch_items.py

# Update prices on Vinted (manual)
python vinted_price_bot.py
```

## 📊 Google Sheets Columns

| Column | You Edit? | What It Does |
|--------|-----------|--------------|
| Item ID | ❌ No | Vinted item identifier |
| Title | ❌ No | Item name |
| Current Price (€) | ❌ No | Current price on Vinted |
| New Price (€) | ❌ No | Calculated new price |
| **Price Change %** | ✅ **YES!** | **Edit this to change prices** |
| URL | ❌ No | Link to item |
| Last Updated | ❌ No | When bot last ran |

## 💰 Price Change Examples

| You Enter | What Happens | Example |
|-----------|--------------|---------|
| `10` | +10% increase | €50 → €55 |
| `-10` | -10% decrease | €50 → €45 |
| `20` | +20% increase | €50 → €60 |
| `-25` | -25% decrease | €50 → €37.50 |
| `0` | No change | €50 → €50 |
| *(blank)* | Use default (10%) | €50 → €55 |

## 📁 Key Files

| File | Purpose |
|------|---------|
| `.env` | Your credentials (never commit!) |
| `service_account.json` | Google API key (never commit!) |
| `fetch_items.py` | Populate sheet with items |
| `vinted_price_bot.py` | Update prices on Vinted |
| `test_connection.py` | Test all connections |
| `setup.py` | Setup wizard |
| `vinted_bot.log` | Bot operation logs |
| `fetch_items.log` | Item fetching logs |

## ⚙️ Environment Variables (.env)

```env
VINTED_EMAIL=your_email@example.com
VINTED_PASSWORD=your_password
VINTED_PROFILE_URL=https://www.vinted.lv/member/YOUR_ID
GOOGLE_SHEET_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON=./service_account.json
DEFAULT_PRICE_CHANGE_PERCENT=10
```

## 🔄 Typical Workflow

### Weekly Routine
```
1. Bot runs automatically Sunday 10 AM UTC
2. Monday: Check Google Sheet
3. Review prices that changed
4. Adjust percentages for next week
5. Items not selling? → Lower % (-5 to -15)
6. Items getting views? → Higher % (+5 to +15)
```

### Adding New Item
```
1. List item on Vinted
2. Run: python fetch_items.py
3. Set custom % in Google Sheet
4. Wait for next bot run (or run manually)
```

### Testing New Price
```
1. Edit % in Google Sheet
2. Run: python vinted_price_bot.py
3. Check Vinted
4. Adjust if needed
```

## 🎯 Pricing Strategies

### Clearance Sale
```
All items: -20%
```

### Seasonal
```
Winter items: +30%
Summer items: -15%
All-season: 0%
```

### Premium
```
Designer: +20%
Vintage: +15%
Regular: +5%
```

### Quick Sale
```
Old listings: -15%
Slow movers: -25%
Popular: +10%
```

## 🔧 Common Issues

| Problem | Quick Fix |
|---------|-----------|
| Items not in sheet | Check VINTED_PROFILE_URL |
| Can't login | Verify email/password in .env |
| Sheet not updating | Check service account shared with sheet |
| Prices not changing | Set Price Change % to non-zero |
| Bot fails | Check logs: vinted_bot.log |

## 🌐 GitHub Actions

### Manual Trigger
```
GitHub → Actions → Vinted Price Update → Run workflow
```

### Schedule (Default)
```
Every Sunday at 10:00 AM UTC
```

### Change Schedule
Edit `.github/workflows/vinted_price_update.yml`:
```yaml
cron: '0 10 * * 0'  # Sunday 10 AM
cron: '0 10 * * 1'  # Monday 10 AM
cron: '0 10 * * *'  # Every day 10 AM
```

### Required Secrets
```
Settings → Secrets → Actions:
- VINTED_EMAIL
- VINTED_PASSWORD
- VINTED_PROFILE_URL
- GOOGLE_SHEET_ID
- GOOGLE_SERVICE_ACCOUNT_JSON
```

## 🆘 Getting Help

### Check Logs
```bash
# View bot logs
cat vinted_bot.log

# View fetch logs
cat fetch_items.log

# Test connections
python test_connection.py
```

### Documentation
- **README.md** - Full setup guide
- **QUICKSTART.md** - 5-minute setup
- **USAGE_GUIDE.md** - Detailed usage examples
- **GITHUB_SECRETS_SETUP.md** - GitHub Actions setup
- **GOOGLE_SHEETS_TEMPLATE.md** - Sheet usage tips

### Still Stuck?
1. Re-run `python test_connection.py`
2. Check logs for errors
3. Review documentation
4. Open GitHub issue

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Initial setup | 10-15 min |
| First item fetch | 2-5 min |
| Customize prices | 5-10 min |
| GitHub deployment | 5-10 min |
| Weekly review | 2-5 min |

## 📈 Success Checklist

- ✅ Installed dependencies
- ✅ Created .env file
- ✅ Got service_account.json
- ✅ Shared sheet with service account
- ✅ Ran test_connection.py (all pass)
- ✅ Ran fetch_items.py (items in sheet)
- ✅ Customized price percentages
- ✅ Tested price update locally
- ✅ Deployed to GitHub Actions
- ✅ Added all GitHub Secrets
- ✅ Workflow runs successfully

## 🎓 Pro Tips

1. **Start small** - Test with 5-10% changes first
2. **Monitor sales** - Track which strategies work
3. **Weekly reviews** - Adjust based on performance
4. **Use 0%** - To pause updates on specific items
5. **Backup sheet** - Make a copy before major changes
6. **Test locally** - Before deploying to GitHub Actions
7. **Check logs** - Always review after bot runs
8. **Be patient** - Let strategy run for 2-3 weeks

---

**Keep this handy!** Bookmark for quick reference. 📌

