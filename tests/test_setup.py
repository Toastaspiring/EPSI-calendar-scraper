"""
Test script to verify all components are working correctly.
Run this to check your setup before syncing to Google Calendar.
"""

import sys
import os


def test_imports():
    """Test if all required modules can be imported."""
    print("Testing imports...")
    tests = []

    # Basic scraping modules
    try:
        import requests
        tests.append(("✓", "requests"))
    except ImportError:
        tests.append(("✗", "requests - Run: pip install requests"))

    try:
        from bs4 import BeautifulSoup
        tests.append(("✓", "beautifulsoup4"))
    except ImportError:
        tests.append(("✗", "beautifulsoup4 - Run: pip install beautifulsoup4"))

    # Google Calendar modules
    try:
        from google.oauth2.credentials import Credentials
        tests.append(("✓", "google-auth"))
    except ImportError:
        tests.append(("✗", "google-auth - Run: pip install google-auth"))

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        tests.append(("✓", "google-auth-oauthlib"))
    except ImportError:
        tests.append(("✗", "google-auth-oauthlib - Run: pip install google-auth-oauthlib"))

    try:
        from googleapiclient.discovery import build
        tests.append(("✓", "google-api-python-client"))
    except ImportError:
        tests.append(("✗", "google-api-python-client - Run: pip install google-api-python-client"))

    for status, msg in tests:
        print(f"  {status} {msg}")

    failed = [t for t in tests if t[0] == "✗"]
    return len(failed) == 0


def test_files():
    """Test if required files exist."""
    print("\nTesting files...")
    tests = []

    # Required files
    files_to_check = [
        ("main.py", True),
        ("google_calendar_sync.py", True),
        ("cookie", True),
        ("credentials.json", False),  # Optional for now
    ]

    for filename, required in files_to_check:
        if os.path.exists(filename):
            tests.append(("✓", filename))
        else:
            if required:
                tests.append(("✗", f"{filename} - REQUIRED"))
            else:
                tests.append(("⚠", f"{filename} - Optional (needed for Google Calendar)"))

    for status, msg in tests:
        print(f"  {status} {msg}")

    failed = [t for t in tests if t[0] == "✗"]
    return len(failed) == 0


def test_cookie_format():
    """Test if cookie file has correct format."""
    print("\nTesting cookie format...")

    if not os.path.exists('cookie'):
        print("  ✗ Cookie file not found")
        return False

    with open('cookie', 'r') as f:
        content = f.read().strip()

    if 'ASP.NET_SessionId=' in content and '.DotNetCasClientAuth=' in content:
        print("  ✓ Cookie format looks good")
        print(f"  ℹ Cookie length: {len(content)} characters")
        return True
    else:
        print("  ✗ Cookie format incorrect")
        print("  Expected format: ASP.NET_SessionId=xxx; .DotNetCasClientAuth=xxx")
        return False


def test_json_parsing():
    """Test if events.json can be parsed (if exists)."""
    print("\nTesting events.json...")

    if not os.path.exists('events.json'):
        print("  ⚠ events.json not found (will be created on first run)")
        return True

    try:
        import json
        with open('events.json', 'r', encoding='utf-8') as f:
            events = json.load(f)

        print(f"  ✓ events.json is valid JSON")
        print(f"  ℹ Found {len(events)} events")

        if len(events) > 0:
            sample = events[0]
            print(f"  ℹ Sample event: {sample.get('course', 'N/A')}")

        return True
    except Exception as e:
        print(f"  ✗ Error parsing events.json: {e}")
        return False


def test_google_credentials():
    """Test if Google credentials are set up."""
    print("\nTesting Google Calendar setup...")

    if not os.path.exists('credentials.json'):
        print("  ⚠ credentials.json not found")
        print("    → This is needed for Google Calendar sync")
        print("    → See GOOGLE_CALENDAR_SETUP.md for instructions")
        return False

    try:
        import json
        with open('credentials.json', 'r') as f:
            creds = json.load(f)

        if 'installed' in creds or 'web' in creds:
            print("  ✓ credentials.json format looks valid")
            return True
        else:
            print("  ✗ credentials.json format incorrect")
            return False
    except Exception as e:
        print(f"  ✗ Error reading credentials.json: {e}")
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Schedule Scraper - System Test")
    print("="*60)

    results = []

    # Run tests
    results.append(("Import test", test_imports()))
    results.append(("File test", test_files()))
    results.append(("Cookie test", test_cookie_format()))
    results.append(("JSON test", test_json_parsing()))
    results.append(("Google credentials test", test_google_credentials()))

    # Summary
    print("\n" + "="*60)
    print("Summary:")
    print("="*60)

    all_passed = True
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status:10} {name}")
        if not passed and "Google" not in name:
            all_passed = False

    print("="*60)

    if all_passed:
        print("\n✓ All critical tests passed!")
        print("  You can run: python main.py")

        if not results[-1][1]:  # Google creds failed
            print("\n⚠ Note: Google Calendar sync not set up yet")
            print("  Follow QUICKSTART.md or GOOGLE_CALENDAR_SETUP.md to enable it")
    else:
        print("\n✗ Some critical tests failed")
        print("  Fix the issues above before running main.py")

    print()


if __name__ == '__main__':
    main()

