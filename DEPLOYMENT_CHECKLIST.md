# Deployment Checklist

Use this checklist to ensure your Vinted Price Bot is properly configured before deployment.

## Pre-Deployment Checklist

### ☐ 1. Google Cloud Setup

- [ ] Created Google Cloud project
- [ ] Enabled Google Sheets API
- [ ] Enabled Google Drive API
- [ ] Created service account
- [ ] Downloaded service account JSON key
- [ ] Saved as `service_account.json` in project root

### ☐ 2. Google Sheets Setup

- [ ] Created new Google Sheet
- [ ] Copied Sheet ID from URL
- [ ] Opened `service_account.json` file
- [ ] Found `client_email` in JSON
- [ ] Shared sheet with service account email (Editor access)
- [ ] Verified sheet access works

### ☐ 3. Vinted Account

- [ ] Have Vinted account credentials
- [ ] Verified login works manually
- [ ] Found your profile URL
- [ ] Confirmed you have items listed
- [ ] **Optional:** Created dedicated account for bot

### ☐ 4. Local Environment

- [ ] Python 3.11+ installed (`python --version`)
- [ ] Git installed (`git --version`)
- [ ] Chrome/Chromium browser installed
- [ ] Cloned repository to local machine

### ☐ 5. Project Configuration

- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Created `.env` file from `.env.example`
- [ ] Filled in all environment variables in `.env`:
  - [ ] `VINTED_EMAIL`
  - [ ] `VINTED_PASSWORD`
  - [ ] `VINTED_PROFILE_URL`
  - [ ] `GOOGLE_SHEET_ID`
  - [ ] `GOOGLE_SERVICE_ACCOUNT_JSON`
  - [ ] `DEFAULT_PRICE_CHANGE_PERCENT`
- [ ] Placed `service_account.json` in project root
- [ ] Verified `.env` and `service_account.json` are in `.gitignore`

### ☐ 6. Local Testing

- [ ] Ran `python test_connection.py`
- [ ] ✅ Environment variables test passed
- [ ] ✅ Selenium WebDriver test passed
- [ ] ✅ Google Sheets connection test passed
- [ ] ✅ Vinted access test passed
- [ ] Ran `python vinted_price_bot.py` successfully
- [ ] Verified items appeared in Google Sheet
- [ ] Checked `vinted_bot.log` for errors

### ☐ 7. GitHub Repository Setup

- [ ] Created GitHub repository (public or private)
- [ ] Pushed code to GitHub
- [ ] Verified `.env` and `service_account.json` NOT pushed
- [ ] Repository has correct structure

### ☐ 8. GitHub Secrets Configuration

Navigate to: **Settings → Secrets and variables → Actions**

- [ ] Added `VINTED_EMAIL`
- [ ] Added `VINTED_PASSWORD`
- [ ] Added `VINTED_PROFILE_URL`
- [ ] Added `GOOGLE_SHEET_ID`
- [ ] Added `GOOGLE_SERVICE_ACCOUNT_JSON` (entire JSON content)
- [ ] Added `DEFAULT_PRICE_CHANGE_PERCENT` (optional)
- [ ] Verified no typos in secret names
- [ ] Verified no extra spaces in secret values

### ☐ 9. GitHub Actions Setup

- [ ] Workflow file exists: `.github/workflows/vinted_price_update.yml`
- [ ] GitHub Actions enabled in repository
- [ ] Reviewed workflow schedule (default: Sunday 10 AM UTC)
- [ ] Customized schedule if needed

### ☐ 10. First Automated Run

- [ ] Go to Actions tab
- [ ] Click "Vinted Price Update" workflow
- [ ] Click "Run workflow" → "Run workflow"
- [ ] Wait for workflow to complete
- [ ] ✅ Workflow shows green checkmark
- [ ] Checked workflow logs for errors
- [ ] Verified items in Google Sheet updated
- [ ] Downloaded and reviewed log artifacts

## Post-Deployment Checklist

### ☐ 11. Verify Automation

- [ ] Workflow runs automatically on schedule
- [ ] Prices update correctly on Vinted
- [ ] Google Sheet stays in sync
- [ ] No errors in logs
- [ ] Email notifications working (if configured)

### ☐ 12. Customize Google Sheet

- [ ] Reviewed default price changes (10%)
- [ ] Customized percentages for specific items
- [ ] Tested different percentage values
- [ ] Verified price calculations are correct
- [ ] Applied your pricing strategy

### ☐ 13. Security Review

- [ ] `.env` file NOT in Git
- [ ] `service_account.json` NOT in Git
- [ ] GitHub Secrets are private
- [ ] No credentials in code
- [ ] No credentials in logs/artifacts
- [ ] Considered using dedicated Vinted account

### ☐ 14. Monitoring Setup

- [ ] Know how to check GitHub Actions logs
- [ ] Know how to download log artifacts
- [ ] Set up calendar reminder to check weekly
- [ ] Documented any custom configurations

### ☐ 15. Documentation Review

- [ ] Read README.md thoroughly
- [ ] Bookmarked troubleshooting section
- [ ] Understand how to modify schedule
- [ ] Know how to update percentages in sheet
- [ ] Familiar with project structure

## Common Issues Resolution

### ❌ Test Failed: Environment Variables

**Fix:**
```bash
# Verify .env exists
ls -la .env

# Check contents (without exposing passwords)
cat .env | grep -v PASSWORD
```

### ❌ Test Failed: Google Sheets

**Fix:**
1. Verify APIs enabled in Google Cloud
2. Check sheet is shared with service account email
3. Verify `GOOGLE_SHEET_ID` is correct
4. Ensure `service_account.json` is valid JSON

### ❌ Test Failed: Selenium

**Fix:**
```bash
# Update Chrome
sudo apt update && sudo apt install google-chrome-stable

# Update dependencies
pip install --upgrade selenium webdriver-manager
```

### ❌ GitHub Actions Failed

**Fix:**
1. Check Actions tab → Failed run → Logs
2. Verify all secrets are added correctly
3. Check `GOOGLE_SERVICE_ACCOUNT_JSON` is complete JSON
4. Ensure no extra spaces in secret values
5. Re-run workflow

### ❌ Prices Not Updating

**Fix:**
1. Check bot logged into Vinted successfully
2. Verify item URLs are correct
3. Check Vinted hasn't changed their UI
4. Review logs for specific errors
5. Test login manually on Vinted

## Maintenance Schedule

### Weekly
- [ ] Check GitHub Actions runs
- [ ] Review Google Sheet for accuracy
- [ ] Verify prices updated on Vinted
- [ ] Check for any error notifications

### Monthly
- [ ] Update Python dependencies
- [ ] Review pricing strategy effectiveness
- [ ] Check for Vinted structure changes
- [ ] Clean up old log artifacts

### As Needed
- [ ] Adjust price percentages
- [ ] Update schedule timing
- [ ] Rotate credentials
- [ ] Update documentation

## Success Criteria

✅ **Bot is working if:**
- Workflow runs without errors
- Items appear in Google Sheet
- Prices update on Vinted
- Timestamps update each run
- Logs show successful operations

## Rollback Plan

If something goes wrong:

1. **Disable Automation:**
   - Go to Actions tab
   - Click "Vinted Price Update"
   - Click "..." → "Disable workflow"

2. **Manual Price Reversion:**
   - Login to Vinted manually
   - Edit items to restore prices
   - Use Google Sheet "Current Price" column as reference

3. **Debug Locally:**
   ```bash
   python test_connection.py
   python vinted_price_bot.py
   ```

4. **Get Help:**
   - Check GitHub Issues
   - Review documentation
   - Check bot logs

## Ready to Deploy?

Count your checkmarks:

- **40+ ✓**: Excellent! You're fully prepared
- **30-39 ✓**: Good! Review missing items
- **20-29 ✓**: Needs work. Complete more steps
- **< 20 ✓**: Not ready. Start with Local Testing section

## Final Verification Command

Run this to verify everything before deploying:

```bash
# Full test suite
python test_connection.py && echo "✅ ALL TESTS PASSED - READY TO DEPLOY!"
```

If all tests pass, you're ready to deploy! 🚀

---

**Need Help?**
- See [README.md](README.md) for detailed instructions
- See [QUICKSTART.md](QUICKSTART.md) for fast setup
- See [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) for Actions setup

**Deployment Date:** _______________  
**Deployed By:** _______________  
**Notes:** _______________

