"""
Setup script for Vinted Price Bot
Helps with initial configuration
"""

import os
import sys

def create_env_file():
    """Create .env file from template"""
    if os.path.exists('.env'):
        response = input(".env file already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Skipping .env creation")
            return
    
    print("\n" + "=" * 60)
    print("Environment Configuration")
    print("=" * 60)
    
    vinted_email = input("Vinted Email: ").strip()
    vinted_password = input("Vinted Password: ").strip()
    vinted_profile_url = input("Vinted Profile URL [https://www.vinted.lv/member/295252411]: ").strip()
    
    if not vinted_profile_url:
        vinted_profile_url = "https://www.vinted.lv/member/295252411"
    
    google_sheet_id = input("Google Sheet ID: ").strip()
    service_account_path = input("Service Account JSON path [./service_account.json]: ").strip()
    
    if not service_account_path:
        service_account_path = "./service_account.json"
    
    default_percent = input("Default Price Change % [10]: ").strip()
    
    if not default_percent:
        default_percent = "10"
    
    env_content = f"""# Vinted Credentials
VINTED_EMAIL={vinted_email}
VINTED_PASSWORD={vinted_password}

# Google Sheets
GOOGLE_SHEET_ID={google_sheet_id}
GOOGLE_SERVICE_ACCOUNT_JSON={service_account_path}

# Settings
VINTED_PROFILE_URL={vinted_profile_url}
DEFAULT_PRICE_CHANGE_PERCENT={default_percent}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")


def check_service_account():
    """Check if service account JSON exists"""
    if not os.path.exists('service_account.json'):
        print("\n⚠️  service_account.json not found!")
        print("\nPlease:")
        print("1. Create a service account in Google Cloud Console")
        print("2. Download the JSON key file")
        print("3. Save it as 'service_account.json' in this directory")
        print("\nSee README.md for detailed instructions.")
        return False
    else:
        print("\n✅ service_account.json found")
        return True


def install_dependencies():
    """Install Python dependencies"""
    response = input("\nInstall Python dependencies? (Y/n): ")
    if response.lower() == 'n':
        print("Skipping dependency installation")
        return
    
    print("\nInstalling dependencies...")
    os.system(f"{sys.executable} -m pip install -r requirements.txt")
    print("✅ Dependencies installed")


def main():
    """Main setup flow"""
    print("=" * 60)
    print("Vinted Price Bot - Setup Wizard")
    print("=" * 60)
    
    print("\nThis wizard will help you set up the bot.")
    print("\nPrerequisites:")
    print("1. Vinted account")
    print("2. Google Cloud project with Sheets API enabled")
    print("3. Service account JSON key file")
    print("4. Google Sheet created and shared with service account")
    
    input("\nPress Enter to continue...")
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Check service account
    check_service_account()
    
    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("1. Make sure service_account.json is in the project directory")
    print("2. Run connection test: python test_connection.py")
    print("3. Run the bot: python vinted_price_bot.py")
    print("4. Set up GitHub Actions (see README.md)")
    
    print("\nFor GitHub Actions:")
    print("1. Push code to GitHub")
    print("2. Add repository secrets (see README.md)")
    print("3. Enable GitHub Actions")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()

