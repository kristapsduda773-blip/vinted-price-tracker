"""
Vinted Price Tracker Bot
Automatically updates Vinted item prices based on Google Sheets configuration
"""

import os
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import gspread
from google.oauth2.service_account import Credentials

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('vinted_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VintedPriceBot:
    """Bot to manage Vinted item prices via Google Sheets"""
    
    def __init__(self):
        """Initialize the bot with environment variables"""
        load_dotenv()
        
        self.vinted_email = os.getenv('VINTED_EMAIL')
        self.vinted_password = os.getenv('VINTED_PASSWORD')
        self.vinted_profile_url = os.getenv('VINTED_PROFILE_URL')
        self.google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.google_creds_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', './service_account.json')
        self.default_percent = float(os.getenv('DEFAULT_PRICE_CHANGE_PERCENT', '10'))
        
        self.driver = None
        self.sheet = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with headless options"""
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        logger.info("WebDriver setup complete")
        
    def setup_google_sheets(self):
        """Initialize Google Sheets connection"""
        logger.info("Setting up Google Sheets connection...")
        
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        creds = Credentials.from_service_account_file(self.google_creds_path, scopes=scope)
        client = gspread.authorize(creds)
        self.sheet = client.open_by_key(self.google_sheet_id).sheet1
        
        logger.info("Google Sheets connection established")
        
    def login_to_vinted(self):
        """Login to Vinted account"""
        logger.info("Logging into Vinted...")
        
        try:
            self.driver.get('https://www.vinted.lv/')
            time.sleep(3)
            
            # Accept cookies if present
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                cookie_button.click()
                time.sleep(1)
            except TimeoutException:
                logger.info("No cookie banner found")
            
            # Click login button
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='header-login-button']"))
            )
            login_button.click()
            time.sleep(2)
            
            # Enter email
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.send_keys(self.vinted_email)
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(self.vinted_password)
            
            # Submit login form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            submit_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            logger.info("Successfully logged into Vinted")
            
        except Exception as e:
            logger.error(f"Failed to login to Vinted: {e}")
            raise
            
    def get_listed_items(self) -> List[Dict]:
        """Scrape user's listed items from Vinted profile"""
        logger.info(f"Fetching items from {self.vinted_profile_url}...")
        
        items = []
        
        try:
            self.driver.get(self.vinted_profile_url)
            time.sleep(3)
            
            # Find all item cards
            item_elements = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='item-box']")
            
            logger.info(f"Found {len(item_elements)} items")
            
            for item_element in item_elements:
                try:
                    # Get item URL
                    link = item_element.find_element(By.TAG_NAME, "a")
                    item_url = link.get_attribute('href')
                    
                    # Get item ID from URL
                    item_id = item_url.split('/')[-1].split('-')[0]
                    
                    # Get title
                    title_element = item_element.find_element(By.CSS_SELECTOR, "[data-testid='item-title']")
                    title = title_element.text
                    
                    # Get price
                    price_element = item_element.find_element(By.CSS_SELECTOR, "[data-testid='item-price']")
                    price_text = price_element.text.replace('€', '').replace(',', '.').strip()
                    
                    # Parse price (handle different formats)
                    try:
                        price = float(price_text.split()[0])
                    except:
                        price = 0.0
                    
                    items.append({
                        'id': item_id,
                        'title': title,
                        'price': price,
                        'url': item_url
                    })
                    
                    logger.info(f"Scraped: {title} - €{price}")
                    
                except Exception as e:
                    logger.warning(f"Failed to parse item: {e}")
                    continue
                    
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch items: {e}")
            raise
            
    def sync_with_google_sheets(self, items: List[Dict]):
        """Sync items with Google Sheets and get price change percentages"""
        logger.info("Syncing with Google Sheets...")
        
        # Setup sheet headers if needed
        try:
            headers = self.sheet.row_values(1)
            if not headers or headers[0] != 'Item ID':
                self.sheet.update('A1:F1', [[
                    'Item ID', 'Title', 'Current Price', 'New Price', 
                    'Price Change %', 'Last Updated'
                ]])
        except:
            self.sheet.update('A1:F1', [[
                'Item ID', 'Title', 'Current Price', 'New Price', 
                'Price Change %', 'Last Updated'
            ]])
        
        # Get existing data
        existing_data = self.sheet.get_all_records()
        existing_dict = {row['Item ID']: row for row in existing_data}
        
        # Prepare updated data
        updated_rows = [['Item ID', 'Title', 'Current Price', 'New Price', 'Price Change %', 'Last Updated']]
        
        for item in items:
            item_id = item['id']
            current_price = item['price']
            
            # Check if item exists in sheet
            if item_id in existing_dict:
                # Get the percentage from sheet, use default if empty
                percent_str = str(existing_dict[item_id].get('Price Change %', '')).strip()
                
                if percent_str and percent_str != '':
                    try:
                        price_change_percent = float(percent_str)
                    except:
                        price_change_percent = self.default_percent
                else:
                    price_change_percent = self.default_percent
            else:
                # New item, use default percentage
                price_change_percent = self.default_percent
            
            # Calculate new price
            new_price = round(current_price * (1 + price_change_percent / 100), 2)
            
            # Store item data with calculated new price
            item['new_price'] = new_price
            item['price_change_percent'] = price_change_percent
            
            updated_rows.append([
                item_id,
                item['title'],
                current_price,
                new_price,
                price_change_percent,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Update entire sheet
        self.sheet.clear()
        self.sheet.update('A1:F' + str(len(updated_rows)), updated_rows)
        
        logger.info(f"Google Sheets updated with {len(items)} items")
        
        return items
        
    def update_item_price(self, item: Dict):
        """Update price for a single item on Vinted"""
        logger.info(f"Updating price for: {item['title']}")
        
        try:
            # Navigate to item page
            self.driver.get(item['url'])
            time.sleep(2)
            
            # Click edit button
            edit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='item-edit-button']"))
            )
            edit_button.click()
            time.sleep(2)
            
            # Find price input
            price_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='price']"))
            )
            
            # Clear and enter new price
            price_input.clear()
            time.sleep(0.5)
            price_input.send_keys(str(item['new_price']))
            time.sleep(1)
            
            # Submit changes
            save_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            save_button.click()
            time.sleep(3)
            
            logger.info(f"Price updated: €{item['price']} → €{item['new_price']} ({item['price_change_percent']:+.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update price for {item['title']}: {e}")
            return False
            
    def run(self):
        """Main execution flow"""
        try:
            logger.info("=" * 60)
            logger.info("Starting Vinted Price Bot")
            logger.info("=" * 60)
            
            # Setup
            self.setup_driver()
            self.setup_google_sheets()
            
            # Login and fetch items
            self.login_to_vinted()
            items = self.get_listed_items()
            
            if not items:
                logger.warning("No items found!")
                return
            
            # Sync with Google Sheets
            items = self.sync_with_google_sheets(items)
            
            # Update prices
            success_count = 0
            for item in items:
                if item['new_price'] != item['price']:
                    if self.update_item_price(item):
                        success_count += 1
                    time.sleep(2)  # Be respectful with requests
                else:
                    logger.info(f"Skipping {item['title']} - no price change needed")
            
            logger.info("=" * 60)
            logger.info(f"Bot completed! Updated {success_count}/{len(items)} items")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"Bot execution failed: {e}")
            raise
            
        finally:
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    bot = VintedPriceBot()
    bot.run()

