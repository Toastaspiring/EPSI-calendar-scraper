import requests
import json
import os
from datetime import datetime, timedelta
import logging
import sys

# Configure logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/schedule_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Base URL for the new Kendo UI scheduler API
BASE_URL = "https://ws-edt-cd.wigorservices.net"
SCHEDULE_PAGE_URL = f"{BASE_URL}/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=louis.marec"
API_URL = f"{BASE_URL}/Home/Get"


def load_cookies():
    """
    Load authentication cookies from file.

    The cookie file should contain cookies in 'name=value; name=value' format.

    Returns:
        Dictionary of cookies
    """
    with open('data/cookie', 'r') as f:
        cookie_string = f.read().strip()

    cookies = {}
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookies[name] = value

    logging.info(f"Loaded cookies: {list(cookies.keys())}")
    return cookies


def get_session_headers():
    """
    Return headers for API requests.
    """
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': SCHEDULE_PAGE_URL,
    }


def verify_auth(session):
    """
    Verify authentication by loading the schedule page.
    Follows CAS redirects, which also warms up the session.

    Returns:
        True if authenticated, False otherwise
    """
    logging.info("Verifying authentication...")
    current_date = datetime.now().strftime('%m/%d/%Y')
    url = f"{SCHEDULE_PAGE_URL}&date={current_date}"

    response = session.get(url, allow_redirects=True)
    response.raise_for_status()

    # Check if we got redirected to a CAS login page
    if 'cas' in response.url.lower() and 'login' in response.url.lower():
        logging.error("Redirected to CAS login page. Cookies have expired!")
        logging.error("Update the 'data/cookie' file with fresh credentials from browser")
        raise Exception("Authentication failed - cookies expired")

    # Check page title for the new scheduler page
    if 'Emploi du temps' in response.text or 'kendoScheduler' in response.text:
        logging.info("Successfully authenticated (new Kendo Scheduler UI)")
        return True

    # Fallback: check if we're NOT on a login page
    if 'Connexion' not in response.text and 'login' not in response.text.lower():
        logging.info("Successfully authenticated")
        return True

    logging.error("Authentication check failed - unexpected page content")
    raise Exception("Authentication failed - unexpected page content")


def fetch_events(date=None):
    """
    Fetch events from the new JSON API.

    The new calendar uses a Kendo UI Scheduler that loads events via
    /Home/Get with dateDebut and dateFin query parameters (ISO 8601 UTC).

    Args:
        date: Target date (datetime object). Defaults to today.

    Returns:
        List of event dictionaries in normalized format
    """
    if date is None:
        date = datetime.now()

    # Compute the week range (Monday to Friday)
    # The Kendo scheduler sends dates in UTC.
    # For Europe/Paris (UTC+1 or UTC+2), the start of Monday is Sunday 22:00 or 23:00 UTC.
    weekday = date.weekday()  # 0=Monday
    monday = date - timedelta(days=weekday)
    friday = monday + timedelta(days=4)

    # Use midnight-to-midnight in local time, shifted to UTC (approx UTC-2 for CEST)
    # The API expects ISO 8601 UTC timestamps. The Kendo scheduler sends:
    # dateDebut = start of Monday (local) in UTC, dateFin = end of Friday (local) in UTC
    # We approximate by sending the full Monday-Friday range with some buffer
    date_debut = (monday - timedelta(hours=2)).strftime('%Y-%m-%dT22:00:00.000Z')
    # Use previous day at 22:00 UTC = midnight CEST
    date_debut = (monday - timedelta(days=1)).strftime('%Y-%m-%dT22:00:00.000Z')
    date_fin = (friday).strftime('%Y-%m-%dT22:00:00.000Z')

    logging.info(f"Target date: {date.strftime('%Y-%m-%d')}")
    logging.info(f"Fetching week: {monday.strftime('%Y-%m-%d')} to {friday.strftime('%Y-%m-%d')}")

    # Load cookies and create session
    cookies = load_cookies()
    session = requests.Session()
    session.cookies.update(cookies)
    session.headers.update(get_session_headers())

    # Verify authentication first (also warms up the session)
    verify_auth(session)

    # Call the JSON API
    params = {
        'sort': '',
        'group': '',
        'filter': '',
        'dateDebut': date_debut,
        'dateFin': date_fin,
    }

    logging.info(f"Fetching events from API: {API_URL}")
    logging.info(f"  dateDebut={date_debut}, dateFin={date_fin}")

    response = session.get(API_URL, params=params)
    response.raise_for_status()

    data = response.json()

    if 'Data' not in data:
        logging.error(f"Unexpected API response format: {list(data.keys())}")
        raise Exception("Unexpected API response - missing 'Data' key")

    raw_events = data['Data']
    logging.info(f"API returned {len(raw_events)} raw events")

    # Save raw API response for debugging
    os.makedirs('data', exist_ok=True)
    with open('data/raw_api.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info("Raw API response saved to data/raw_api.json")

    # Normalize events to a consistent format
    events = normalize_events(raw_events)
    return events


def normalize_events(raw_events):
    """
    Convert raw API events to a normalized format compatible with
    both the old format and calendar sync scripts.

    The new API returns:
        - Commentaire: course name (displayed as title)
        - Start/End: ISO 8601 timestamps with timezone
        - NomProf: professor name
        - Salles: room
        - LibelleGroupe: group label
        - CoursMixteInfoBulle: mode (Presentiel/Distanciel/Mixte)
        - ColorRed/Green/Blue: event color
        - TeamsUrl: Teams link HTML (or null)
        - Title: group name (not the course name!)
        - Matiere: often "COMMENTAIRE" when course is in Commentaire field

    Returns:
        List of normalized event dictionaries
    """
    events = []

    for raw in raw_events:
        # Use Commentaire as course name (this is what the Kendo template uses)
        course = raw.get('Commentaire') or raw.get('Matiere') or 'Unknown'

        # Parse ISO timestamps
        start_str = raw.get('Start', '')
        end_str = raw.get('End', '')

        event = {
            'course': course,
            'start': start_str,
            'end': end_str,
            'professor': raw.get('NomProf') or 'N/A',
            'group': raw.get('LibelleGroupe') or raw.get('Title') or 'N/A',
            'room': raw.get('Salles') or 'N/A',
            'mode': raw.get('CoursMixteInfoBulle') or 'N/A',
        }

        # Build color hex from RGB
        r = raw.get('ColorRed')
        g = raw.get('ColorGreen')
        b = raw.get('ColorBlue')
        if r is not None and g is not None and b is not None:
            event['color'] = f'#{r:02X}{g:02X}{b:02X}'

        # Backward compatibility: date and time fields
        # Parse start/end ISO strings to extract date (MM/DD/YYYY) and time (HH:MM - HH:MM)
        try:
            start_dt = datetime.fromisoformat(start_str)
            end_dt = datetime.fromisoformat(end_str)
            event['date'] = start_dt.strftime('%m/%d/%Y')
            event['time'] = f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}"
        except (ValueError, TypeError):
            logging.warning(f"Could not parse dates for event: {course}")

        # Teams links
        teams_url = raw.get('TeamsUrl')
        if teams_url:
            event['teams_url'] = teams_url

        events.append(event)

    return events


def print_events(events):
    """
    Log events in a readable format.
    """
    if not events:
        logging.warning("No events found.")
        return

    logging.info(f"Found {len(events)} events:")

    for i, event in enumerate(events, 1):
        logging.info(f"Event {i}: {event.get('course', 'N/A')} on {event.get('date', 'N/A')} at {event.get('time', 'N/A')}")
        logging.debug(f"  Professor: {event.get('professor', 'N/A')}")
        logging.debug(f"  Room: {event.get('room', 'N/A')}")
        logging.debug(f"  Mode: {event.get('mode', 'N/A')}")


def save_events_to_json(events, filename='data/events.json'):
    """
    Save extracted events to a JSON file.

    Args:
        events: List of event dictionaries
        filename: Output filename (default: data/events.json)
    """
    os.makedirs('data', exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=2, ensure_ascii=False)
    logging.info(f"Events saved to {filename}")


if __name__ == '__main__':
    import argparse

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Scrape schedule and optionally sync to Google/Outlook Calendar')
    parser.add_argument('--no-sync', action='store_true', help='Skip Calendar sync')
    parser.add_argument('--sync-only', action='store_true', help='Only sync existing events.json, skip scraping')
    parser.add_argument('--provider', type=str, choices=['GOOGLE', 'OUTLOOK', 'BOTH'],
                        help='Calendar provider (overrides CALENDAR_PROVIDER env var)')
    args = parser.parse_args()

    # Determine provider
    provider = args.provider or os.environ.get('CALENDAR_PROVIDER', 'GOOGLE')
    provider = provider.upper()

    try:
        if not args.sync_only:
            # Fetch schedule via API
            logging.info("Starting schedule scraper...")
            events = fetch_events()
            print_events(events)
            save_events_to_json(events)
            logging.info("Scraping completed successfully")

        # Sync to Calendar (unless --no-sync flag is set)
        if not args.no_sync:
            # Sync Google
            if provider in ['GOOGLE', 'BOTH']:
                try:
                    from scripts.google_calendar_sync import sync_events_to_calendar
                    logging.info("Starting Google Calendar sync...")
                    created_count = sync_events_to_calendar()
                    logging.info(f"Google Calendar sync completed: {created_count} events created")
                except ImportError:
                    logging.error("Google Calendar module not available.")
                except Exception as e:
                    logging.error(f"Error syncing to Google Calendar: {e}")

            # Sync Outlook
            if provider in ['OUTLOOK', 'BOTH']:
                try:
                    from scripts.outlook_calendar_sync import sync_events_to_outlook
                    logging.info("Starting Outlook Calendar sync...")
                    # Load events
                    with open('data/events.json', 'r', encoding='utf-8') as f:
                        events_data = json.load(f)

                    created_count = sync_events_to_outlook(events_data)
                    logging.info(f"Outlook Calendar sync completed: {created_count} events created")
                except ImportError:
                    logging.error("Outlook module not available. Install O365.")
                except Exception as e:
                    logging.error(f"Error syncing to Outlook: {e}")
        else:
            logging.info("Skipping Calendar sync (--no-sync flag set)")

        logging.info("All operations completed successfully")
        sys.exit(0)

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
