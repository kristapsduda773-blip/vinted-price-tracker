"""
Fetch and populate Google Sheets with current Vinted items
Run this script first to see all your items before price updates
"""

import os
import time
import logging
from datetime import datetime
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
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
        logging.FileHandler('fetch_items.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class VintedItemFetcher:
    """Fetch and populate Google Sheets with Vinted items"""
    
    def __init__(self):
        """Initialize the fetcher"""
        load_dotenv()
        
        self.vinted_profile_url = os.getenv('VINTED_PROFILE_URL')
        self.google_sheet_id = os.getenv('GOOGLE_SHEET_ID')
        self.google_creds_path = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON', './service_account.json')
        self.default_percent = float(os.getenv('DEFAULT_PRICE_CHANGE_PERCENT', '10'))
        
        self.driver = None
        self.sheet = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver"""
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
        
    def get_listed_items(self):
        """Scrape user's listed items from Vinted profile"""
        logger.info(f"Fetching items from {self.vinted_profile_url}...")
        
        items = []
        
        try:
            self.driver.get(self.vinted_profile_url)
            time.sleep(5)  # Wait for page to load
            
            # Try to accept cookies if present
            try:
                cookie_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                cookie_button.click()
                time.sleep(1)
            except TimeoutException:
                logger.info("No cookie banner found")
            
            # Scroll to load all items (lazy loading)
            logger.info("Scrolling to load all items...")
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            # Find all item cards - try multiple selectors
            item_elements = []
            
            # Try different selectors that Vinted might use
            selectors = [
                "[data-testid*='item-box']",
                ".feed-grid__item",
                ".item-box",
                "div[class*='ItemBox']",
                "a[href*='/items/']"
            ]
            
            for selector in selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements:
                        item_elements = elements
                        logger.info(f"Found {len(elements)} items using selector: {selector}")
                        break
                except:
                    continue
            
            if not item_elements:
                logger.warning("No items found with any selector. Trying alternative method...")
                # Fallback: find all links that contain /items/
                item_elements = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='/items/']")
                logger.info(f"Found {len(item_elements)} item links as fallback")
            
            logger.info(f"Processing {len(item_elements)} items...")
            
            seen_ids = set()  # Track unique items
            
            for idx, item_element in enumerate(item_elements, 1):
                try:
                    # Get item URL
                    link = item_element if item_element.tag_name == 'a' else item_element.find_element(By.TAG_NAME, "a")
                    item_url = link.get_attribute('href')
                    
                    if not item_url or '/items/' not in item_url:
                        continue
                    
                    # Get item ID from URL (e.g., /items/4322916107-...)
                    item_id = item_url.split('/items/')[-1].split('-')[0]
                    
                    # Skip duplicates
                    if item_id in seen_ids:
                        continue
                    seen_ids.add(item_id)
                    
                    # Get title - try multiple approaches
                    title = "Unknown Title"
                    try:
                        # Try data-testid
                        title_element = item_element.find_element(By.CSS_SELECTOR, "[data-testid='item-title']")
                        title = title_element.text
                    except:
                        try:
                            # Try common class names
                            title_element = item_element.find_element(By.CSS_SELECTOR, ".item-box__title, .ItemBox_title, [class*='title']")
                            title = title_element.text
                        except:
                            try:
                                # Use URL as fallback
                                title = item_url.split('/')[-1].replace('-', ' ').title()
                            except:
                                pass
                    
                    # Get price - try multiple approaches
                    price = 0.0
                    try:
                        price_element = item_element.find_element(By.CSS_SELECTOR, "[data-testid='item-price']")
                        price_text = price_element.text.replace('€', '').replace(',', '.').strip()
                    except:
                        try:
                            price_element = item_element.find_element(By.CSS_SELECTOR, ".item-box__price, .ItemBox_price, [class*='price']")
                            price_text = price_element.text.replace('€', '').replace(',', '.').strip()
                        except:
                            price_text = "0"
                    
                    # Parse price
                    try:
                        # Handle formats like "50.00", "50,00", "50.00 €", etc.
                        price_clean = price_text.split()[0].replace('€', '').replace(',', '.')
                        price = float(price_clean)
                    except:
                        price = 0.0
                    
                    items.append({
                        'id': item_id,
                        'title': title.strip() if title else f"Item {item_id}",
                        'price': price,
                        'url': item_url
                    })
                    
                    logger.info(f"  [{idx}] {title[:50]} - €{price} (ID: {item_id})")
                    
                except Exception as e:
                    logger.debug(f"Failed to parse item {idx}: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(items)} unique items")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch items: {e}")
            raise
            
    def populate_google_sheets(self, items):
        """Populate Google Sheets with fetched items"""
        logger.info("Populating Google Sheets...")
        
        if not items:
            logger.warning("No items to populate!")
            return
        
        # Prepare sheet data
        headers = ['Item ID', 'Title', 'Current Price (€)', 'New Price (€)', 'Price Change %', 'URL', 'Last Updated']
        rows = [headers]
        
        for item in items:
            new_price = round(item['price'] * (1 + self.default_percent / 100), 2)
            
            rows.append([
                item['id'],
                item['title'],
                item['price'],
                new_price,
                self.default_percent,
                item['url'],
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        # Clear and update sheet
        self.sheet.clear()
        self.sheet.update(f'A1:G{len(rows)}', rows)
        
        # Format header row (bold)
        self.sheet.format('A1:G1', {
            'textFormat': {'bold': True},
            'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
        })
        
        # Freeze header row
        self.sheet.freeze(rows=1)
        
        # Auto-resize columns
        self.sheet.columns_auto_resize(0, 6)
        
        logger.info(f"✅ Successfully populated sheet with {len(items)} items")
        logger.info(f"📊 Sheet URL: https://docs.google.com/spreadsheets/d/{self.google_sheet_id}")
        
    def run(self):
        """Main execution flow"""
        try:
            logger.info("=" * 70)
            logger.info("Vinted Item Fetcher - Populating Google Sheets")
            logger.info("=" * 70)
            
            # Setup
            self.setup_driver()
            self.setup_google_sheets()
            
            # Fetch items
            items = self.get_listed_items()
            
            if not items:
                logger.error("❌ No items found! Check your profile URL and make sure you have items listed.")
                return
            
            # Populate sheet
            self.populate_google_sheets(items)
            
            logger.info("=" * 70)
            logger.info(f"✅ SUCCESS! {len(items)} items added to Google Sheets")
            logger.info("=" * 70)
            logger.info("\n📝 Next Steps:")
            logger.info("1. Open your Google Sheet")
            logger.info("2. Review the items and prices")
            logger.info("3. Edit the 'Price Change %' column for each item:")
            logger.info("   - Positive numbers increase price (e.g., 10 = +10%)")
            logger.info("   - Negative numbers decrease price (e.g., -15 = -15%)")
            logger.info("   - Leave blank to use default (10%)")
            logger.info("4. Run the price update bot or wait for weekly automation")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"❌ Failed to fetch items: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise
            
        finally:
            if self.driver:
                self.driver.quit()


if __name__ == "__main__":
    fetcher = VintedItemFetcher()
    fetcher.run()

