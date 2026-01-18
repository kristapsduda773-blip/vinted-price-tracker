"""
Quick setup script - Creates .env file with your Google Sheet
"""

import os

# Your Google Sheet ID
SHEET_ID = "1PO8zzalK5Fvfjub3HyB5E0bKcnMxvPbDSH_XpSgd7RU"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"

print("=" * 70)
print("Vinted Price Tracker - Quick Setup")
print("=" * 70)
print()

# Check if .env exists
if os.path.exists('.env'):
    response = input(".env file already exists. Overwrite? (y/N): ")
    if response.lower() != 'y':
        print("Setup cancelled. Your existing .env file was not changed.")
        exit(0)

print("Creating .env file with your configuration...")
print()

# Get user input
print("Enter your details:")
vinted_email = input("Vinted Email: ").strip()
vinted_password = input("Vinted Password: ").strip()

# Use default profile URL
vinted_profile = "https://www.vinted.lv/member/295252411"
print(f"Vinted Profile URL: {vinted_profile}")

# Service account path
service_account = "./service_account.json"
print(f"Service Account JSON: {service_account}")

# Default percentage
default_percent = input("Default Price Change % [10]: ").strip()
if not default_percent:
    default_percent = "10"

print()
print("Creating .env file...")

# Create .env content
env_content = f"""# Vinted Credentials
VINTED_EMAIL={vinted_email}
VINTED_PASSWORD={vinted_password}

# Google Sheets
GOOGLE_SHEET_ID={SHEET_ID}
GOOGLE_SERVICE_ACCOUNT_JSON={service_account}

# Settings
VINTED_PROFILE_URL={vinted_profile}
DEFAULT_PRICE_CHANGE_PERCENT={default_percent}
"""

# Write .env file
with open('.env', 'w') as f:
    f.write(env_content)

print("✅ .env file created successfully!")
print()
print("=" * 70)
print("IMPORTANT - Share Your Google Sheet!")
print("=" * 70)
print()
print("You MUST share your Google Sheet with the service account:")
print()
print("1. Open service_account.json file")
print("2. Find the 'client_email' field")
print("3. Copy that email address (looks like: xxx@xxx.iam.gserviceaccount.com)")
print()
print("4. Open your Google Sheet:")
print(f"   {SHEET_URL}")
print()
print("5. Click the 'Share' button (top right)")
print("6. Paste the service account email")
print("7. Make sure role is 'Editor'")
print("8. UNCHECK 'Notify people' (it's a bot, not a person)")
print("9. Click 'Share' or 'Send'")
print()
print("=" * 70)
print("Next Steps:")
print("=" * 70)
print()
print("1. Share the Google Sheet (see instructions above)")
print("2. Place service_account.json in this directory")
print("3. Test connection: python test_connection.py")
print("4. Fetch your items: python fetch_items.py")
print("5. Customize percentages in the Google Sheet")
print("6. Run bot: python vinted_price_bot.py")
print()
print("=" * 70)

