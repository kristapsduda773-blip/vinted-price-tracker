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
from selenium.webdriver.common.keys import Keys
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
        self.default_percent = float(os.getenv('DEFAULT_PRICE_CHANGE_PERCENT', '-2'))  # Negative to LOWER prices
        
        # Extract profile ID from URL (e.g., "https://www.vinted.lv/member/295252411" -> "295252411")
        if self.vinted_profile_url:
            self.profile_id = self.vinted_profile_url.rstrip('/').split('/')[-1]
        else:
            self.profile_id = None
        
        self.driver = None
        self.sheet = None
        
    def setup_driver(self):
        """Initialize Chrome WebDriver with headless options"""
        logger.info("Setting up Chrome WebDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # Get ChromeDriver path
            import os
            driver_path = ChromeDriverManager().install()
            logger.info(f"ChromeDriver manager returned: {driver_path}")
            
            # Fix for webdriver-manager bug - find the actual chromedriver binary
            actual_driver = None
            
            # Check if it's directly the chromedriver file (exact filename match)
            filename = os.path.basename(driver_path)
            if os.path.isfile(driver_path) and (filename == 'chromedriver' or filename == 'chromedriver.exe'):
                actual_driver = driver_path
            else:
                # Navigate up to find the base directory
                base_dir = driver_path
                
                # If the path points to a non-chromedriver file, go to parent directory
                if os.path.isfile(base_dir):
                    base_dir = os.path.dirname(base_dir)
                
                # Search for chromedriver in this directory and subdirectories
                logger.info(f"Searching for chromedriver in: {base_dir}")
                
                # Common locations
                possible_paths = [
                    os.path.join(base_dir, 'chromedriver'),
                    os.path.join(base_dir, 'chromedriver.exe'),
                    os.path.join(base_dir, 'chromedriver-linux64', 'chromedriver'),
                    os.path.join(base_dir, 'chromedriver-win64', 'chromedriver.exe'),
                    os.path.join(base_dir, 'chromedriver-mac64', 'chromedriver'),
                ]
                
                # Try each possible path
                for path in possible_paths:
                    if os.path.isfile(path):
                        actual_driver = path
                        logger.info(f"Found chromedriver at: {actual_driver}")
                        break
                
                # If still not found, walk the directory tree
                if not actual_driver:
                    for root, dirs, files in os.walk(base_dir):
                        if 'chromedriver' in files:
                            actual_driver = os.path.join(root, 'chromedriver')
                            logger.info(f"Found chromedriver via walk at: {actual_driver}")
                            break
                        elif 'chromedriver.exe' in files:
                            actual_driver = os.path.join(root, 'chromedriver.exe')
                            logger.info(f"Found chromedriver.exe via walk at: {actual_driver}")
                            break
            
            if not actual_driver or not os.path.isfile(actual_driver):
                raise Exception(f"Could not find chromedriver binary in {driver_path}")
            
            # Make sure it's executable on Linux/Mac
            if not actual_driver.endswith('.exe'):
                os.chmod(actual_driver, 0o755)
            
            logger.info(f"Using ChromeDriver at: {actual_driver}")
            service = Service(actual_driver)
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("WebDriver setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup WebDriver: {e}")
            raise
        
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
            # Go to the signup/login page (Vinted uses same page for both)
            self.driver.get('https://www.vinted.lv/member/signup/select_type?ref_url=%2F')
            time.sleep(3)
            
            logger.info(f"Loaded page: {self.driver.current_url}")
            
            # Close any modal overlays (domain selector, etc.)
            try:
                # Look for close button on modal
                modal_close_selectors = [
                    (By.CSS_SELECTOR, "[data-testid*='modal'] button[aria-label='Close']"),
                    (By.CSS_SELECTOR, ".ReactModal__Overlay button[aria-label='Close']"),
                    (By.CSS_SELECTOR, "[class*='modal'] button"),
                    (By.XPATH, "//button[contains(@aria-label, 'Close')]"),
                ]
                
                for by, selector in modal_close_selectors:
                    try:
                        close_button = WebDriverWait(self.driver, 2).until(
                            EC.element_to_be_clickable((by, selector))
                        )
                        close_button.click()
                        logger.info("Closed modal overlay")
                        time.sleep(1)
                        break
                    except:
                        continue
            except:
                logger.info("No modal to close")
            
            # Accept cookies if present
            try:
                cookie_button = WebDriverWait(self.driver, 3).until(
                    EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
                )
                cookie_button.click()
                logger.info("Accepted cookies")
                time.sleep(2)
            except:
                logger.info("No cookie banner found")
            
            # STEP 1: Click "Pieteikties" span
            logger.info("STEP 1: Clicking 'Pieteikties'...")
            login_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Pieteikties')]"))
            )
            self.driver.execute_script("arguments[0].click();", login_link)
            logger.info("✓ Clicked 'Pieteikties'")
            time.sleep(4)
            
            # STEP 2: Click "e-pasta adrese" span
            logger.info("STEP 2: Clicking 'e-pasta adrese'...")
            email_option_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'e-pasta')]"))
            )
            self.driver.execute_script("arguments[0].click();", email_option_button)
            logger.info("✓ Clicked 'e-pasta adrese'")
            time.sleep(3)
            
            # STEP 3: Fill email and password
            logger.info("STEP 3: Filling login form...")
            email_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='E-pasta'], input[id='username'], input[id='email']"))
            )
            
            if not email_input:
                # Debug: List all input elements on the page
                try:
                    all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    logger.error(f"Could not find email input. Found {len(all_inputs)} input elements total:")
                    for idx, inp in enumerate(all_inputs[:10]):  # Show first 10
                        input_type = inp.get_attribute('type')
                        input_name = inp.get_attribute('name')
                        input_id = inp.get_attribute('id')
                        input_placeholder = inp.get_attribute('placeholder')
                        logger.error(f"  Input {idx+1}: type={input_type}, name={input_name}, id={input_id}, placeholder={input_placeholder}")
                except Exception as e:
                    logger.error(f"Could not list inputs: {e}")
                
                # Save page source for debugging
                with open('/tmp/vinted_login_page.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.error("Page source saved to /tmp/vinted_login_page.html")
                raise Exception("Email input not found")
            
            # Fill email with proper event triggering
            email_input.clear()
            email_input.send_keys(self.vinted_email)
            # Trigger input and change events
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, email_input)
            logger.info("✓ Email entered")
            time.sleep(1)
            
            password_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input.clear()
            password_input.send_keys(self.vinted_password)
            # Trigger input and change events
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, password_input)
            logger.info("✓ Password entered")
            time.sleep(2)  # Wait a bit longer for any validation
            
            # Check for captcha
            try:
                captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='captcha'], [id*='captcha'], iframe[src*='captcha'], iframe[src*='recaptcha']")
                if captcha_elements:
                    logger.error("⚠️ CAPTCHA detected! Waiting 30 seconds for manual solving...")
                    logger.error("Please solve the CAPTCHA in the browser if running locally")
                    time.sleep(30)
            except:
                pass
            
            # Store the current URL before submitting
            pre_submit_url = self.driver.current_url
            
            # Submit login form - try to find login/submit button
            submit_button = None
            submit_selectors = [
                (By.CSS_SELECTOR, "button[type='submit']"),
                (By.XPATH, "//button[contains(., 'Login') or contains(., 'Pieteikt') or contains(., 'Sign in')]"),
                (By.CSS_SELECTOR, "button.auth__button, button[class*='auth']"),
            ]
            
            for by, selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(by, selector)
                    if submit_button:
                        logger.info(f"Found submit button with: {selector}")
                        break
                except:
                    pass
            
            if not submit_button:
                logger.error("Could not find submit button")
                raise Exception("Submit button not found")
            
            # Try multiple submission methods
            submission_methods = [
                ("JavaScript form submit", lambda: self.driver.execute_script("""
                    let form = document.querySelector('form');
                    if (form) {
                        form.submit();
                        return true;
                    }
                    return false;
                """)),
                ("Button click", lambda: (submit_button.click(), True)[1]),
                ("JavaScript button click", lambda: (self.driver.execute_script("arguments[0].click();", submit_button), True)[1]),
                ("Enter key", lambda: (password_input.send_keys(Keys.RETURN), True)[1]),
            ]
            
            logger.info("Attempting form submission...")
            redirect_success = False
            
            for method_name, submit_func in submission_methods:
                if redirect_success:
                    break
                    
                try:
                    logger.info(f"Trying: {method_name}")
                    submit_func()
                    time.sleep(2)  # Brief wait after submission
                    
                    # Check for immediate validation errors
                    try:
                        errors = self.driver.find_elements(By.CSS_SELECTOR, ".form__error, .error, [class*='error']")
                        visible_errors = [e.text for e in errors if e.is_displayed() and e.text.strip()]
                        if visible_errors:
                            logger.warning(f"Validation errors: {', '.join(visible_errors)}")
                            continue  # Try next method
                    except:
                        pass
                    
                    # Wait for redirect
                    logger.info(f"Waiting for redirect after {method_name}...")
                    try:
                        WebDriverWait(self.driver, 10).until(
                            lambda d: '/signup' not in d.current_url and '/login' not in d.current_url and d.current_url != pre_submit_url
                        )
                        logger.info(f"✓ Redirected to: {self.driver.current_url}")
                        redirect_success = True
                        break
                    except:
                        logger.warning(f"{method_name} did not trigger redirect")
                        
                except Exception as e:
                    logger.warning(f"{method_name} failed: {e}")
                    continue
            
            time.sleep(3)  # Additional wait for page to stabilize
            
            # Verify login success
            current_url = self.driver.current_url
            logger.info(f"After login, current URL: {current_url}")
            
            # Check and log cookies to verify session is saved
            try:
                cookies = self.driver.get_cookies()
                session_cookies = [c for c in cookies if 'session' in c['name'].lower() or 'auth' in c['name'].lower() or '_vinted' in c['name']]
                if session_cookies:
                    logger.info(f"✓ Found {len(session_cookies)} session cookie(s)")
                else:
                    logger.warning("⚠️ No session cookies found - login may not persist")
                    logger.info(f"Total cookies: {len(cookies)}")
            except Exception as e:
                logger.warning(f"Could not check cookies: {e}")
            
            # Check if we're still on login/signup pages
            if any(x in current_url for x in ['/login', '/signup', '/signin']):
                # Still on login/signup page - check for errors
                logger.error("⚠️ Still on login/signup page after submission!")
                
                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".form__error, .error, [class*='error'], [class*='Error']")
                    visible_errors = [el.text for el in error_elements if el.is_displayed() and el.text.strip()]
                    if visible_errors:
                        logger.error(f"Login error messages: {' | '.join(visible_errors)}")
                except:
                    pass
                
                # Check form validation state
                try:
                    email_input_check = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='E-pasta'], input[id='username']")
                    password_input_check = self.driver.find_element(By.ID, "password")
                    
                    email_value = email_input_check.get_attribute('value')
                    password_value = password_input_check.get_attribute('value')
                    
                    logger.error(f"Debug: Email filled: {bool(email_value)}, Password filled: {bool(password_value)}")
                    logger.error(f"Debug: Email field valid: {email_input_check.get_attribute('aria-invalid') != 'true'}")
                    logger.error(f"Debug: Password field valid: {password_input_check.get_attribute('aria-invalid') != 'true'}")
                except Exception as e:
                    logger.error(f"Could not check form state: {e}")
                
                # Check for submit button state
                try:
                    if submit_button:
                        is_disabled = submit_button.get_attribute('disabled')
                        is_aria_disabled = submit_button.get_attribute('aria-disabled')
                        logger.error(f"Debug: Submit button disabled: {is_disabled}, aria-disabled: {is_aria_disabled}")
                except:
                    pass
                
                # Debug: Check if form is still visible
                try:
                    email_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                    password_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
                    logger.error(f"Debug: Email fields found: {len(email_fields)}, Password fields: {len(password_fields)}")
                except:
                    pass
                
                with open('/tmp/vinted_login_failed.html', 'w', encoding='utf-8') as f:
                    f.write(self.driver.page_source)
                logger.error("Login verification failed. Page source saved.")
                
                # More helpful error message
                if visible_errors:
                    raise Exception(f"Login failed with errors: {', '.join(visible_errors)}")
                else:
                    raise Exception("Login failed - form not submitting. This could be: 1) Wrong credentials, 2) Captcha required, 3) Anti-bot detection, 4) Form validation issue")
            else:
                logger.info("✓ Successfully logged in!")
                # Wait longer to ensure session cookies are fully set
                logger.info("Waiting for session to stabilize...")
                time.sleep(5)
            
        except Exception as e:
            logger.error(f"Failed to login to Vinted: {e}")
            raise
            
    def get_listed_items(self) -> List[Dict]:
        """Scrape user's listed items from Vinted profile"""
        logger.info(f"Fetching items from {self.vinted_profile_url}...")
        
        items = []
        
        try:
            self.driver.get(self.vinted_profile_url)
            time.sleep(5)
            
            # Scrape items WHILE scrolling (Vinted unloads items as you scroll down)
            logger.info("Scrolling and collecting items incrementally...")
            
            processed_ids = set()  # Track which items we've already scraped
            scroll_attempts = 0
            max_scrolls = 20
            no_new_items_count = 0
            
            while scroll_attempts < max_scrolls and no_new_items_count < 3:
                # Find all currently visible item links
                item_links = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid*='--overlay-link']")
                
                items_found_this_scroll = 0
                
                for link in item_links:
                    try:
                        # Get item ID from data-testid (format: "product-item-id-7819896031--overlay-link")
                        testid = link.get_attribute('data-testid')
                        if testid and 'product-item-id-' in testid:
                            item_id = testid.replace('product-item-id-', '').split('--')[0]
                        else:
                            item_url = link.get_attribute('href')
                            if not item_url or '/items/' not in item_url:
                                continue
                            item_id = item_url.split('/items/')[-1].split('-')[0]
                        
                        # Skip if already processed
                        if item_id in processed_ids:
                            continue
                        
                        # Get item URL
                        item_url = link.get_attribute('href')
                        if not item_url or '/items/' not in item_url:
                            continue
                        
                        # Get title from the title attribute
                        title = link.get_attribute('title')
                        clean_title = title.split(',')[0] if title else f"Item {item_id}"
                        
                        # Get price - search within the parent container, not the whole page
                        price = 0.0
                        try:
                            # Find the parent container that holds both link and price
                            parent = link.find_element(By.XPATH, '../..')
                            # Now find price within this container
                            price_element = parent.find_element(By.CSS_SELECTOR, f"[data-testid='product-item-id-{item_id}--price-text']")
                            
                            # Wait for text to be present (Vinted lazy-loads prices)
                            price_text = price_element.text.strip()
                            attempts = 0
                            while not price_text and attempts < 5:
                                time.sleep(0.1)  # Wait for lazy load
                                price_text = price_element.text.strip()
                                attempts += 1
                            
                            if price_text:
                                # Remove € symbol and parse (e.g., "€13.00" or "13.00")
                                price_text = price_text.replace('€', '').replace(',', '.').strip()
                                price = float(price_text)
                            else:
                                # Price element exists but still empty - item may not be fully loaded yet
                                # Try one more time with JavaScript
                                try:
                                    price_text = self.driver.execute_script("return arguments[0].textContent;", price_element).strip()
                                    if price_text:
                                        price_text = price_text.replace('€', '').replace(',', '.').strip()
                                        price = float(price_text)
                                    else:
                                        logger.warning(f"Price element found but empty for item {item_id}")
                                        price = 0.0
                                except:
                                    logger.warning(f"Price element found but empty for item {item_id}")
                                    price = 0.0
                        except NoSuchElementException:
                            logger.warning(f"Price element not found for item {item_id}")
                            price = 0.0
                        except Exception as e:
                            logger.warning(f"Error getting price for item {item_id}: {e}")
                            price = 0.0
                        
                        # Ensure URL is absolute
                        if not item_url.startswith('http'):
                            item_url = f"https://www.vinted.lv{item_url}"
                        
                        items.append({
                            'id': item_id,
                            'title': clean_title,
                            'price': price,
                            'url': item_url
                        })
                        
                        processed_ids.add(item_id)
                        items_found_this_scroll += 1
                        logger.info(f"Scraped: {clean_title} - €{price} (ID: {item_id})")
                        
                    except Exception as e:
                        logger.warning(f"Failed to parse item link: {e}")
                        continue
                
                # Track if we found new items
                if items_found_this_scroll == 0:
                    no_new_items_count += 1
                else:
                    no_new_items_count = 0
                
                logger.info(f"Scroll {scroll_attempts + 1}: Found {items_found_this_scroll} new items (Total: {len(items)})")
                
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                scroll_attempts += 1
            
            logger.info(f"Completed scrolling after {scroll_attempts} scrolls")
            
            logger.info(f"Successfully scraped {len(items)} items")
            return items
            
        except Exception as e:
            logger.error(f"Failed to fetch items: {e}")
            raise
            
    def sync_with_google_sheets(self, items: List[Dict]):
        """Sync items with Google Sheets and get price change percentages"""
        logger.info("Syncing with Google Sheets...")
        
        # Get existing data before setting headers (in case sheet has old format)
        existing_dict = {}
        try:
            existing_data = self.sheet.get_all_records()
            existing_dict = {str(row.get('Item ID', '')): row for row in existing_data if row.get('Item ID')}
        except Exception as e:
            logger.warning(f"Could not read existing sheet data (may have duplicate headers): {e}")
            # Try to read manually by getting all values
            try:
                all_values = self.sheet.get_all_values()
                if len(all_values) > 1:
                    # Find the header row with 'Item ID'
                    header_row = None
                    for idx, row in enumerate(all_values):
                        if 'Item ID' in row:
                            header_row = idx
                            headers = row
                            break
                    
                    if header_row is not None and len(all_values) > header_row + 1:
                        # Parse manually
                        item_id_col = headers.index('Item ID')
                        for row in all_values[header_row + 1:]:
                            if len(row) > item_id_col and row[item_id_col]:
                                item_id = str(row[item_id_col])
                                existing_dict[item_id] = {
                                    'Item ID': row[item_id_col] if len(row) > item_id_col else '',
                                    'URL': row[headers.index('URL')] if 'URL' in headers and len(row) > headers.index('URL') else '',
                                    'Title': row[headers.index('Title')] if 'Title' in headers and len(row) > headers.index('Title') else '',
                                    'Current Price': row[headers.index('Current Price')] if 'Current Price' in headers and len(row) > headers.index('Current Price') else 0,
                                    'New Price': row[headers.index('New Price')] if 'New Price' in headers and len(row) > headers.index('New Price') else 0,
                                    'Price Change %': row[headers.index('Price Change %')] if 'Price Change %' in headers and len(row) > headers.index('Price Change %') else '',
                                    'Floor Price': row[headers.index('Floor Price')] if 'Floor Price' in headers and len(row) > headers.index('Floor Price') else '',
                                    'Status': row[headers.index('Status')] if 'Status' in headers and len(row) > headers.index('Status') else '',
                                    'Last Updated': row[headers.index('Last Updated')] if 'Last Updated' in headers and len(row) > headers.index('Last Updated') else ''
                                }
                        logger.info(f"Manually parsed {len(existing_dict)} existing items from sheet")
            except Exception as e2:
                logger.warning(f"Could not manually parse sheet data: {e2}")
                existing_dict = {}
        
        # Get current item IDs from Vinted
        current_item_ids = {item['id'] for item in items}
        
        # Detect changes
        new_items = []
        updated_items = []
        removed_item_ids = []
        
        # Check for new and updated items
        for item in items:
            item_id = item['id']
            if item_id in existing_dict:
                updated_items.append(item_id)
            else:
                new_items.append(item_id)
        
        # Check for removed items (in sheet but not on Vinted)
        for item_id in existing_dict.keys():
            if item_id not in current_item_ids:
                removed_item_ids.append(item_id)
        
        # Log changes
        if new_items:
            logger.info(f"🆕 New items found: {len(new_items)} (prices will NOT change until next run)")
            for item_id in new_items:
                item = next((i for i in items if i['id'] == item_id), None)
                if item:
                    logger.info(f"   + {item['title']} (€{item['price']})")
        
        if removed_item_ids:
            logger.info(f"🗑️  Removed items (likely sold): {len(removed_item_ids)}")
            for item_id in removed_item_ids:
                if item_id in existing_dict:
                    logger.info(f"   - {existing_dict[item_id].get('Title', 'Unknown')}")
        
        if not new_items and not removed_item_ids:
            logger.info("ℹ️  No new or removed items")
        
        # Get all existing rows to find row numbers for updates
        try:
            all_values = self.sheet.get_all_values()
            header_row_idx = None
            for idx, row in enumerate(all_values):
                if 'Item ID' in row:
                    header_row_idx = idx
                    break
            
            if header_row_idx is None:
                # No header found, need to create sheet from scratch
                logger.info("No header found, creating new sheet...")
                self.sheet.clear()
                header = ['Item ID', 'URL', 'Title', 'Current Price', 'New Price', 'Floor Price', 'Price Change %', 'Status', 'Last Updated']
                self.sheet.update(values=[header], range_name='A1')
                header_row_idx = 0
                existing_row_map = {}  # item_id -> row_number (1-based, including header)
            else:
                # Map existing item IDs to their row numbers (1-based, including header)
                headers = all_values[header_row_idx]
                item_id_col = headers.index('Item ID') if 'Item ID' in headers else 0
                existing_row_map = {}
                for idx, row in enumerate(all_values[header_row_idx + 1:], start=header_row_idx + 2):  # +2 because 1-based and skip header
                    if len(row) > item_id_col and row[item_id_col]:
                        existing_row_map[str(row[item_id_col])] = idx
        except Exception as e:
            logger.warning(f"Could not read existing rows: {e}")
            existing_row_map = {}
            header_row_idx = 0
        
        # Process items: update existing rows or prepare new rows
        rows_to_update = {}  # row_number -> row_data
        new_rows_to_append = []  # List of new rows to append
        
        # Process current items from Vinted
        for item in items:
            item_id = item['id']
            current_price = item['price']
            is_new_item = item_id not in existing_dict
            
            # Check if item exists in sheet
            if not is_new_item:
                # EXISTING ITEM - use sheet settings
                # Get the percentage from sheet, use default if empty
                percent_str = str(existing_dict[item_id].get('Price Change %', '')).strip()
                
                if percent_str and percent_str != '':
                    try:
                        price_change_percent = float(percent_str)
                    except:
                        price_change_percent = self.default_percent
                else:
                    price_change_percent = self.default_percent
                
                # Get floor price if set
                floor_price_str = str(existing_dict[item_id].get('Floor Price', '')).strip()
                if floor_price_str and floor_price_str != '':
                    try:
                        floor_price = float(floor_price_str)
                    except:
                        floor_price = None
                else:
                    floor_price = None
                
                status = 'Active'
            else:
                # NEW ITEM - Don't change price on first discovery
                price_change_percent = 0  # 0% change = no price update
                floor_price = None
                status = '🆕 New'
                logger.info(f"   🆕 NEW ITEM DISCOVERED: {item['title']} - Price will NOT be changed this run")
            
            # Calculate new price
            new_price = round(current_price * (1 + price_change_percent / 100), 2)
            
            # Apply floor price if set
            if floor_price is not None and new_price < floor_price:
                logger.info(f"   Floor price applied for {item['title']}: €{new_price:.2f} → €{floor_price:.2f}")
                new_price = floor_price
            
            # Store item data with calculated new price
            item['new_price'] = new_price
            item['price_change_percent'] = price_change_percent
            item['floor_price'] = floor_price if floor_price is not None else ''
            item['is_new_discovery'] = is_new_item  # Flag for later use
            
            row_data = [
                item_id,
                item.get('url', ''),
                item['title'],
                current_price,
                new_price,
                floor_price if floor_price is not None else '',
                price_change_percent if not is_new_item else self.default_percent,
                status,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
            
            # If item exists in sheet, check if data changed before updating
            if item_id in existing_row_map:
                # Only update if data actually changed
                old_data = existing_dict[item_id]
                
                # Safely convert prices to float (handle strings, empty values, etc.)
                try:
                    old_price = float(str(old_data.get('Current Price', 0) or 0).replace(',', '.'))
                except:
                    old_price = 0.0
                
                try:
                    old_new_price = float(str(old_data.get('New Price', 0) or 0).replace(',', '.'))
                except:
                    old_new_price = 0.0
                
                old_status = str(old_data.get('Status', '')).strip()
                
                # Check if anything meaningful changed (ignore timestamp)
                # Only update if the CURRENT PRICE changed (not just recalculated new_price)
                # Use tolerance to account for rounding differences
                price_changed = abs(old_price - current_price) > 0.05  # 5 cent tolerance
                status_changed = old_status != status
                
                # Also check if title or URL changed (shouldn't happen, but just in case)
                old_title = str(old_data.get('Title', '')).strip()
                old_url = str(old_data.get('URL', '')).strip()
                title_changed = old_title != item['title']
                url_changed = old_url != item.get('url', '')
                
                # Only update if CURRENT PRICE or STATUS changed (not just recalculated new_price)
                # This prevents unnecessary updates when only order changes
                if price_changed or status_changed or title_changed or url_changed:
                    # Data changed - add to update list
                    changes = []
                    if price_changed:
                        changes.append(f"current_price: {old_price}→{current_price}")
                    if status_changed:
                        changes.append(f"status: {old_status}→{status}")
                    if title_changed:
                        changes.append(f"title changed")
                    if url_changed:
                        changes.append(f"url changed")
                    logger.debug(f"Item {item_id} changed: {', '.join(changes)}")
                    rows_to_update[existing_row_map[item_id]] = row_data
                # else: skip update - no changes needed
            else:
                # New item - always append
                new_rows_to_append.append(row_data)
        
        # Process removed items - update their status to sold/removed
        for item_id in removed_item_ids:
            if item_id in existing_dict:
                old_data = existing_dict[item_id]
                if item_id in existing_row_map:
                    # Update existing row to mark as sold
                    rows_to_update[existing_row_map[item_id]] = [
                        item_id,
                        old_data.get('URL', ''),
                        old_data.get('Title', 'Unknown'),
                        old_data.get('Current Price', 0),
                        old_data.get('New Price', 0),
                        old_data.get('Floor Price', ''),
                        0,  # Set Price Change % to 0 for sold items
                        '❌ Sold/Removed',
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
        
        # Update existing rows in batches to avoid rate limits (60 writes/min = 1 per second)
        if rows_to_update:
            logger.info(f"Updating {len(rows_to_update)} rows that changed (out of {len(existing_row_map)} total)...")
            sorted_rows = sorted(rows_to_update.items())
            
            # Group consecutive rows together for batch updates
            groups = []
            if sorted_rows:
                current_group = [sorted_rows[0]]
                for i in range(1, len(sorted_rows)):
                    if sorted_rows[i][0] == sorted_rows[i-1][0] + 1:
                        # Consecutive row - add to current group
                        current_group.append(sorted_rows[i])
                    else:
                        # Gap found - start new group
                        groups.append(current_group)
                        current_group = [sorted_rows[i]]
                groups.append(current_group)
            
            # Update each group (consecutive rows can be updated in one API call)
            for group_idx, group in enumerate(groups):
                if len(group) == 1:
                    # Single row
                    row_num, row_data = group[0]
                    range_name = f'A{row_num}:I{row_num}'
                    self.sheet.update(values=[row_data], range_name=range_name)
                else:
                    # Multiple consecutive rows - update in one call
                    min_row = group[0][0]
                    max_row = group[-1][0]
                    range_name = f'A{min_row}:I{max_row}'
                    row_dict = {row_num: row_data for row_num, row_data in group}
                    batch_values = [row_dict[r] for r in range(min_row, max_row + 1)]
                    self.sheet.update(values=batch_values, range_name=range_name)
                
                # Add delay between groups to stay under rate limit (1 request per second)
                if group_idx < len(groups) - 1:
                    time.sleep(1.1)  # Wait 1.1 seconds between groups
        
        # Append new rows
        if new_rows_to_append:
            logger.info(f"Appending {len(new_rows_to_append)} new rows...")
            # Find the last row
            try:
                all_values = self.sheet.get_all_values()
                last_row = len(all_values)
            except:
                last_row = 1  # Header row
            
            # Append all new rows at once
            range_name = f'A{last_row + 1}:I{last_row + len(new_rows_to_append)}'
            self.sheet.update(values=new_rows_to_append, range_name=range_name)
        
        # Format sold/removed items in red
        if removed_item_ids:
            logger.info(f"Formatting {len(removed_item_ids)} sold items in red...")
            try:
                for item_id in removed_item_ids:
                    if item_id in existing_row_map:
                        row_num = existing_row_map[item_id]
                        # Format entire row in red with strikethrough
                        self.sheet.format(f'A{row_num}:I{row_num}', {
                            'backgroundColor': {'red': 1.0, 'green': 0.8, 'blue': 0.8},  # Light red
                            'textFormat': {
                                'strikethrough': True,
                                'foregroundColor': {'red': 0.6, 'green': 0.0, 'blue': 0.0}  # Dark red text
                            }
                        })
            except Exception as e:
                logger.warning(f"Could not format sold items: {e}")
        
        logger.info("✓ Sheet data updated (only new rows added, existing rows updated)")
        
        # Count new discoveries
        new_discovery_count = len([i for i in items if i.get('is_new_discovery', False)])
        
        # Calculate total rows in sheet
        total_rows = len(existing_row_map) + len(new_rows_to_append)  # Existing + new
        # Removed items are already in existing_row_map, so they're counted
        
        logger.info(f"📊 Google Sheets updated:")
        logger.info(f"   Active items: {len(items)}")
        if new_discovery_count > 0:
            logger.info(f"   🆕 New discoveries: {new_discovery_count}")
        if removed_item_ids:
            logger.info(f"   🗑️  Removed items: {len(removed_item_ids)}")
        logger.info(f"   Total rows in sheet: {total_rows}")
        
        return items, existing_dict
        
    def update_item_price(self, item: Dict, existing_dict: Dict = None):
        """Update price for a single item on Vinted"""
        logger.info(f"Updating price for: {item['title']}")
        
        try:
            # Get URL from sheet if available, otherwise use item URL
            item_id = item['id']
            if existing_dict and item_id in existing_dict:
                item_url = existing_dict[item_id].get('URL', '') or item.get('url', '')
            else:
                item_url = item.get('url', '')
            
            if not item_url:
                logger.error(f"No URL found for item {item_id}")
                return False
            
            logger.info(f"Using URL from sheet: {item_url}")
            
            # Establish session by navigating to homepage first
            logger.info("Navigating to homepage to establish session...")
            self.driver.get("https://www.vinted.lv")
            time.sleep(2)
            
            # Verify we're logged in (not redirected to login)
            current_url = self.driver.current_url
            if any(x in current_url for x in ['/login', '/signup', '/signin']):
                logger.error("⚠️ Session lost - redirected to login from homepage!")
                return False
            logger.info("✓ Session verified on homepage")
            
            # Now navigate to item page
            logger.info(f"Navigating to item page: {item_url}")
            self.driver.get(item_url)
            time.sleep(3)  # Wait for item page to load
            
            # Verify we're on item page (not redirected to login)
            current_url = self.driver.current_url
            if any(x in current_url for x in ['/login', '/signup', '/signin']):
                logger.error("⚠️ Redirected to login from item page - session invalid!")
                return False
            logger.info("✓ Item page loaded successfully")
            
            # Now navigate to edit page using normal navigation (not JavaScript)
            edit_url = item_url.rstrip('/') + '/edit'
            logger.info(f"Navigating to edit page: {edit_url}")
            self.driver.get(edit_url)
            time.sleep(2)  # Wait for navigation
            
            # Wait for edit page to load
            WebDriverWait(self.driver, 15).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            time.sleep(3)  # Additional wait for dynamic content
            
            # DEBUG: Print HTML structure to help locate edit button (check entire page, not just sidebar)
            # Check if we're on the edit page
            current_url = self.driver.current_url
            logger.info(f"Current URL: {current_url}")
            
            if '/edit' not in current_url:
                # We got redirected - check if it's login page
                if any(x in current_url for x in ['/login', '/signup', '/signin']):
                    logger.error("⚠️ Redirected to login page - session expired or invalid!")
                    return False
                else:
                    logger.error(f"⚠️ Could not access edit page - redirected to: {current_url}")
                    logger.error("This item may not belong to the logged-in account!")
                    return False
            
            logger.info("✓ Successfully accessed edit page")
            
            # Find price input - using exact ID and data-testid
            logger.info("Looking for price input...")
            price_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input#price[data-testid='price-input--input']"))
            )
            current_value = price_input.get_attribute('value')
            logger.info(f"Price input found with current value: {current_value}")
            
            # Clear and enter new price (remove € symbol if present)
            price_input.clear()
            time.sleep(0.5)
            
            # Format price as Vinted expects (just the number, e.g., "24.50")
            new_price_str = f"{item['new_price']:.2f}"
            price_input.send_keys(new_price_str)
            logger.info(f"Entered new price: €{new_price_str}")
            time.sleep(1)
            
            # Click Save button - using exact data-testid
            logger.info("Looking for Save button...")
            save_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='upload-form-save-button']"))
            )
            save_button.click()
            logger.info("Save button clicked")
            
            time.sleep(3)
            
            percent_value = float(item.get('price_change_percent', 0))
            logger.info(f"✓ Price updated: €{item['price']:.2f} → €{item['new_price']:.2f} ({percent_value:.1f}%)")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update price for {item['title']}: {e}")
            # Save screenshot on error
            try:
                self.driver.save_screenshot(f'/tmp/price_update_error_{item["id"]}.png')
                logger.info(f"Error screenshot saved for item {item['id']}")
            except:
                pass
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
            
            # Fetch items from PUBLIC profile (no login needed)
            logger.info("Fetching items from public profile (no login required)...")
            items = self.get_listed_items()
            
            if not items:
                logger.warning("No items found!")
                return
            
            # Sync with Google Sheets
            items, existing_dict = self.sync_with_google_sheets(items)
            
            # Now login for price updates
            logger.info("\n" + "=" * 60)
            logger.info("Logging in to update prices...")
            logger.info("=" * 60)
            try:
                self.login_to_vinted()
                can_update = True
            except Exception as e:
                logger.error(f"Login failed: {e}")
                logger.warning("⚠️  Items saved to Google Sheet, but price updates skipped")
                can_update = False
            
            # Update prices (TESTING MODE: Only last item)
            if can_update:
                logger.info("⚠️  TESTING MODE: Only updating last item with price change")
                success_count = 0
                
                # Find items that need price changes (exclude new discoveries and items with no change)
                items_to_update = [
                    item for item in items 
                    if item['new_price'] != item['price'] 
                    and not item.get('is_new_discovery', False)  # Skip newly discovered items
                ]
                
                if not items_to_update:
                    logger.info("No items need price updates")
                else:
                    # Get the LAST item that needs updating
                    last_item = items_to_update[-1]
                    
                    logger.info(f"🧪 Testing price update on LAST item: {last_item['title']}")
                    logger.info(f"   Current price: €{last_item['price']:.2f}")
                    logger.info(f"   New price: €{last_item['new_price']:.2f}")
                    percent_value = float(last_item.get('price_change_percent', 0))
                    logger.info(f"   Change: {percent_value:.1f}%")
                    
                    if self.update_item_price(last_item, existing_dict):
                        success_count += 1
                
                logger.info("=" * 60)
                logger.info(f"Bot completed! Updated {success_count}/{len(items_to_update) if items_to_update else 0} items (test mode)")
                logger.info(f"⚠️  TEST MODE: {len(items) - len(items_to_update)} items skipped")
                logger.info("=" * 60)
            else:
                logger.info("=" * 60)
                logger.info("Bot completed! Items synced to Google Sheet (no price updates)")
                logger.info("=" * 60)
                
        except Exception as e:
            logger.error(f"Bot execution failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("WebDriver closed")

if __name__ == "__main__":
    bot = VintedPriceBot()
    bot.run()

