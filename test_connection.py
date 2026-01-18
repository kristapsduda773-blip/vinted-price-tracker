"""
Test script to verify Vinted and Google Sheets connections
Run this before deploying to GitHub Actions
"""

import os
import sys
from dotenv import load_dotenv

def test_env_variables():
    """Check if all required environment variables are set"""
    print("Testing environment variables...")
    load_dotenv()
    
    required_vars = [
        'VINTED_EMAIL',
        'VINTED_PASSWORD',
        'VINTED_PROFILE_URL',
        'GOOGLE_SHEET_ID',
        'GOOGLE_SERVICE_ACCOUNT_JSON'
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
            print(f"❌ {var}: Not set")
        else:
            # Hide sensitive values
            display_value = value[:10] + "..." if len(value) > 10 else "***"
            print(f"✅ {var}: {display_value}")
    
    if missing:
        print(f"\n❌ Missing variables: {', '.join(missing)}")
        return False
    
    print("\n✅ All environment variables are set!\n")
    return True


def test_google_sheets():
    """Test Google Sheets connection"""
    print("Testing Google Sheets connection...")
    
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        
        load_dotenv()
        
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', './service_account.json')
        sheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        if not os.path.exists(creds_path):
            print(f"❌ Service account file not found: {creds_path}")
            return False
        
        creds = Credentials.from_service_account_file(creds_path, scopes=scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(sheet_id)
        
        print(f"✅ Connected to sheet: {sheet.title}")
        print(f"   Worksheets: {[ws.title for ws in sheet.worksheets()]}")
        
        # Try to read first row
        worksheet = sheet.sheet1
        first_row = worksheet.row_values(1)
        print(f"   First row: {first_row if first_row else 'Empty'}")
        
        print("\n✅ Google Sheets connection successful!\n")
        return True
        
    except FileNotFoundError:
        print("❌ service_account.json file not found!")
        print("   Make sure the file exists in the project root")
        return False
    except Exception as e:
        print(f"❌ Google Sheets connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Check if Google Sheets API is enabled")
        print("2. Check if Google Drive API is enabled")
        print("3. Verify the sheet is shared with the service account email")
        print("4. Verify GOOGLE_SHEET_ID is correct")
        return False


def test_selenium():
    """Test Selenium WebDriver setup"""
    print("Testing Selenium WebDriver...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        print("   Installing ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        print("   Starting Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("   Testing navigation...")
        driver.get('https://www.google.com')
        
        title = driver.title
        driver.quit()
        
        print(f"✅ Selenium working! (Navigated to: {title})")
        print("\n✅ Selenium setup successful!\n")
        return True
        
    except Exception as e:
        print(f"❌ Selenium setup failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Chrome/Chromium is installed")
        print("2. Try running: pip install --upgrade selenium webdriver-manager")
        return False


def test_vinted_access():
    """Test basic Vinted access (without login)"""
    print("Testing Vinted access...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        import time
        
        load_dotenv()
        profile_url = os.getenv('VINTED_PROFILE_URL')
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"   Navigating to: {profile_url}")
        driver.get(profile_url)
        time.sleep(3)
        
        title = driver.title
        print(f"✅ Page loaded: {title}")
        
        driver.quit()
        print("\n✅ Vinted access successful!\n")
        return True
        
    except Exception as e:
        print(f"❌ Vinted access failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Vinted Price Bot - Connection Test")
    print("=" * 60)
    print()
    
    results = {
        'Environment Variables': test_env_variables(),
        'Selenium WebDriver': test_selenium(),
        'Google Sheets': test_google_sheets(),
        'Vinted Access': test_vinted_access()
    }
    
    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print("=" * 60)
    
    if all(results.values()):
        print("\n🎉 All tests passed! You're ready to run the bot.")
        print("\nNext steps:")
        print("1. Run locally: python vinted_price_bot.py")
        print("2. Set up GitHub Secrets (see README.md)")
        print("3. Deploy to GitHub Actions")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        print("See README.md for setup instructions.")
        sys.exit(1)


if __name__ == "__main__":
    main()

