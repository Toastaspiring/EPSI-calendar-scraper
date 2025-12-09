"""
Automatic WigorServices Login Script
Simulates browser login and captures authentication cookies.

This script uses Selenium to automate the login process and extract cookies,
eliminating the need to manually copy them from browser DevTools.
"""

import json
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configuration
WIGOR_URL = "https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=louis.marec"
CAS_LOGIN_URL = "https://cas-p.wigorservices.net/cas/login"
COOKIE_FILE = "data/cookie"
COOKIE_JSON_FILE = "data/cookies_full.json"


def setup_driver(headless=False):
    """
    Set up Chrome WebDriver with appropriate options.

    Args:
        headless: If True, runs browser in headless mode (no GUI)

    Returns:
        WebDriver instance
    """
    chrome_options = Options()

    if headless:
        chrome_options.add_argument('--headless')

    # Additional options for stability
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')

    # User agent to appear as a real browser
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        logging.info("Chrome WebDriver initialized successfully")
        return driver
    except Exception as e:
        logging.error(f"Failed to initialize WebDriver: {e}")
        logging.error("Make sure Chrome and ChromeDriver are installed")
        raise


def perform_login(driver, username, password):
    """
    Perform the CAS login process.

    Args:
        driver: WebDriver instance
        username: Your username
        password: Your password

    Returns:
        True if login successful, False otherwise
    """
    try:
        logging.info("Navigating to WigorServices...")
        driver.get(WIGOR_URL)

        # Wait for redirect to CAS login page
        time.sleep(2)

        # Check if we're on the CAS login page
        if "cas" not in driver.current_url.lower():
            logging.info("Already authenticated (no redirect to login)")
            return True

        logging.info(f"Redirected to CAS login: {driver.current_url}")

        # Wait for login form (form id="fm1")
        logging.info("Waiting for login form...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fm1"))
        )

        # Find username and password fields
        username_field = driver.find_element(By.ID, "username")
        password_field = driver.find_element(By.ID, "password")

        # Fill in credentials
        logging.info(f"Entering credentials for user: {username}")
        username_field.clear()
        username_field.send_keys(username)

        password_field.clear()
        password_field.send_keys(password)

        # Find submit button by ID
        logging.info("Looking for submit button...")
        try:
            submit_button = driver.find_element(By.ID, "submitBtn")
            logging.info("Found submit button with ID 'submitBtn'")
        except NoSuchElementException:
            # Fallback: try by name
            try:
                submit_button = driver.find_element(By.NAME, "submitBtn")
                logging.info("Found submit button by name 'submitBtn'")
            except NoSuchElementException:
                # Last resort: submit the form directly
                logging.info("Submit button not found, submitting form directly...")
                password_field.submit()
                submit_button = None

        if submit_button:
            # Submit form
            logging.info("Submitting login form...")
            submit_button.click()

        # Wait for redirect after login
        time.sleep(3)

        # Check if login was successful
        if "cas" in driver.current_url.lower() and "login" in driver.current_url.lower():
            logging.error("Still on login page - login may have failed")

            # Check for error messages
            try:
                error_elements = driver.find_elements(By.CLASS_NAME, "errors")
                if error_elements:
                    error_text = error_elements[0].text
                    logging.error(f"Login error: {error_text}")
            except:
                pass

            return False

        logging.info(f"Login successful! Redirected to: {driver.current_url}")
        return True

    except TimeoutException:
        logging.error("Timeout waiting for login page elements")
        return False
    except NoSuchElementException as e:
        logging.error(f"Could not find login form element: {e}")
        return False
    except Exception as e:
        logging.error(f"Unexpected error during login: {e}")
        return False


def extract_cookies(driver):
    """
    Extract cookies from the browser session.

    Args:
        driver: WebDriver instance

    Returns:
        Dictionary of cookies
    """
    logging.info("Extracting cookies...")

    # Get all cookies
    all_cookies = driver.get_cookies()

    # Log cookies found
    logging.info(f"Found {len(all_cookies)} cookies")
    for cookie in all_cookies:
        logging.debug(f"  - {cookie['name']}: {cookie['value'][:20]}...")

    # Filter for important cookies
    important_cookies = {
        'ASP.NET_SessionId': None,
        '.DotNetCasClientAuth': None
    }

    for cookie in all_cookies:
        if cookie['name'] in important_cookies:
            important_cookies[cookie['name']] = cookie['value']

    return all_cookies, important_cookies


def save_cookies(all_cookies, important_cookies):
    """
    Save cookies to files.

    Args:
        all_cookies: List of all cookies
        important_cookies: Dictionary of important cookies
    """
    # Ensure data directory exists
    import os
    os.makedirs('data', exist_ok=True)

    # Save all cookies as JSON (for reference)
    with open(COOKIE_JSON_FILE, 'w') as f:
        json.dump(all_cookies, f, indent=2)
    logging.info(f"All cookies saved to {COOKIE_JSON_FILE}")

    # Save important cookies in the format needed by main.py
    if important_cookies['ASP.NET_SessionId'] and important_cookies['.DotNetCasClientAuth']:
        cookie_string = f"ASP.NET_SessionId={important_cookies['ASP.NET_SessionId']}; .DotNetCasClientAuth={important_cookies['.DotNetCasClientAuth']}"

        with open(COOKIE_FILE, 'w') as f:
            f.write(cookie_string)

        logging.info(f"Cookie file saved to {COOKIE_FILE}")
        logging.info(f"Cookie preview: {cookie_string[:80]}...")

        return True
    else:
        logging.error("Required cookies not found!")
        logging.error(f"ASP.NET_SessionId: {'Found' if important_cookies['ASP.NET_SessionId'] else 'Missing'}")
        logging.error(f".DotNetCasClientAuth: {'Found' if important_cookies['.DotNetCasClientAuth'] else 'Missing'}")
        return False


def test_cookies(driver):
    """
    Test if the captured cookies work by fetching the schedule page.

    Args:
        driver: WebDriver instance

    Returns:
        True if cookies work, False otherwise
    """
    try:
        logging.info("Testing cookies by fetching schedule page...")

        # Try to access the schedule page
        current_date = datetime.now().strftime('%m/%d/%Y')
        test_url = f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=louis.marec&date={current_date}"

        driver.get(test_url)
        time.sleep(2)

        # Check if we got redirected to login (cookies don't work)
        if "cas" in driver.current_url.lower() and "login" in driver.current_url.lower():
            logging.error("Cookies don't work - redirected to login")
            return False

        # Check if we see schedule content
        page_source = driver.page_source.lower()
        if "connexion" in page_source and "authentication" in page_source:
            logging.error("Cookies don't work - seeing login page")
            return False

        logging.info("✓ Cookies work! Successfully accessed schedule page")
        return True

    except Exception as e:
        logging.error(f"Error testing cookies: {e}")
        return False


def main():
    """
    Main function to automate login and capture cookies.
    """
    print("="*60)
    print("WigorServices Automatic Login & Cookie Generator")
    print("="*60)
    print()

    # Get credentials
    print("Enter your WigorServices credentials:")
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    if not username or not password:
        logging.error("Username and password are required")
        return 1

    headless_input = input("\nRun in headless mode (no browser window)? (y/n): ").strip().lower()
    headless = headless_input == 'y'

    driver = None

    try:
        # Setup WebDriver
        driver = setup_driver(headless=headless)

        # Perform login
        login_success = perform_login(driver, username, password)

        if not login_success:
            logging.error("Login failed. Please check your credentials.")
            return 1

        # Wait a bit for cookies to be set
        time.sleep(2)

        # Extract cookies
        all_cookies, important_cookies = extract_cookies(driver)

        # Save cookies
        save_success = save_cookies(all_cookies, important_cookies)

        if not save_success:
            logging.error("Failed to save cookies")
            return 1

        # Test cookies
        test_success = test_cookies(driver)

        print()
        print("="*60)
        if test_success:
            print("✓ SUCCESS! Cookies captured and verified")
            print("="*60)
            print()
            print(f"Cookie file created: {COOKIE_FILE}")
            print(f"Full cookies saved: {COOKIE_JSON_FILE}")
            print()
            print("You can now run: python main.py")
            print()
            print("Note: Cookies will expire after your session ends.")
            print("      Run this script again when they expire.")
            return 0
        else:
            print("⚠ WARNING: Cookies captured but failed verification")
            print("="*60)
            print()
            print("The cookie file was created, but may not work.")
            print("You can try running: python main.py")
            return 1

    except Exception as e:
        logging.error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        # Close browser
        if driver:
            logging.info("Closing browser...")
            driver.quit()


if __name__ == '__main__':
    import sys
    exit_code = main()
    sys.exit(exit_code)

