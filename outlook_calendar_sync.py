"""
Outlook Calendar Integration for Schedule Scraper

This module handles authentication and syncing of events to Outlook Calendar
using the O365 python library (Microsoft Graph API).
"""

import json
import os
import base64
import logging
from datetime import datetime, timezone
from O365 import Account, FileSystemTokenBackend

# Helper to check if running in a non-interactive environment (CI/CD)
# In this case, we rely on environment variables to provide the token
def is_running_in_ci():
    return os.environ.get('CI') == 'true' or os.environ.get('GITHUB_ACTIONS') == 'true'

def authenticate_outlook_calendar():
    """
    Authenticate with Outlook Calendar API.

    Returns:
        O365.Account object or None if authentication fails
    """
    client_id = os.environ.get('OUTLOOK_CLIENT_ID')
    client_secret = os.environ.get('OUTLOOK_CLIENT_SECRET')

    # Try to load credentials from environment variable if individual vars are not set
    # This matches the pattern in google_calendar_sync.py but for O365 we usually just need id/secret
    if not (client_id and client_secret):
        if os.environ.get('OUTLOOK_CREDENTIALS_JSON_BASE64'):
             try:
                 creds_json = base64.b64decode(os.environ['OUTLOOK_CREDENTIALS_JSON_BASE64']).decode('utf-8')
                 creds = json.loads(creds_json)
                 client_id = creds.get('client_id')
                 client_secret = creds.get('client_secret')
                 logging.info("Loaded Outlook credentials from environment variable")
             except Exception as e:
                 logging.error(f"Failed to decode OUTLOOK_CREDENTIALS_JSON_BASE64: {e}")

    if not client_id or not client_secret:
        logging.error("Outlook Client ID and Client Secret are required.")
        logging.error("Set OUTLOOK_CLIENT_ID and OUTLOOK_CLIENT_SECRET environment variables.")
        return None

    credentials = (client_id, client_secret)

    # Handle token storage
    # We use FileSystemTokenBackend but we might need to pre-populate it from env vars
    token_filename = 'o365_token.txt'
    token_backend = FileSystemTokenBackend(token_path='.', token_filename=token_filename)

    # Restore token from environment variable if it doesn't exist
    if not os.path.exists(token_filename) and os.environ.get('OUTLOOK_TOKEN_TXT_BASE64'):
        try:
            token_data = base64.b64decode(os.environ['OUTLOOK_TOKEN_TXT_BASE64'])
            with open(token_filename, 'wb') as f:
                f.write(token_data)
            logging.info(f"Restored {token_filename} from environment variable")
        except Exception as e:
            logging.error(f"Failed to decode OUTLOOK_TOKEN_TXT_BASE64: {e}")

    account = Account(credentials, token_backend=token_backend)

    if not account.is_authenticated:
        # If not authenticated, we can't do interactive login in a background script
        # So we fail unless we are in an interactive session (which we assume we aren't for sync)
        logging.warning("Outlook account is not authenticated.")
        if not is_running_in_ci():
             logging.info("Attempting interactive authentication...")
             # Scopes for reading and writing calendar
             scopes = ['basic', 'calendar_all']
             if account.authenticate(scopes=scopes):
                 logging.info("Authenticated successfully!")
             else:
                 logging.error("Authentication failed.")
                 return None
        else:
             logging.error("Cannot authenticate interactively in CI/CD environment.")
             return None

    return account

def parse_event_datetime(date_str, time_str):
    """
    Parse date and time strings into datetime objects.
    Duplicated from google_calendar_sync.py to keep modules independent.

    Args:
        date_str: Date string (e.g., "11/17/2025")
        time_str: Time range string (e.g., "09:00 - 12:30")

    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    # Parse the time range
    start_time, end_time = time_str.split(' - ')

    # Parse date (format: MM/DD/YYYY or DD/MM/YYYY)
    # Assuming MM/DD/YYYY based on the URL pattern
    date_parts = date_str.split('/')
    month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])

    # Parse start time
    start_hour, start_min = map(int, start_time.split(':'))
    start_dt = datetime(year, month, day, start_hour, start_min)

    # Parse end time
    end_hour, end_min = map(int, end_time.split(':'))
    end_dt = datetime(year, month, day, end_hour, end_min)

    return start_dt, end_dt

def create_calendar_event(schedule, event_data, event_date):
    """
    Create a single event in Outlook Calendar.

    Args:
        schedule: O365 Schedule object
        event_data: Dictionary containing event information
        event_date: Date string for the event

    Returns:
        True if successful, False otherwise
    """
    try:
        start_dt, end_dt = parse_event_datetime(event_date, event_data['time'])

        # Set timezone to Europe/Paris
        import pytz
        tz = pytz.timezone('Europe/Paris')

        # Localize the naive datetimes
        start_dt = tz.localize(start_dt)
        end_dt = tz.localize(end_dt)

        # Check for duplicates
        # Query events in the time range
        q = schedule.new_query('start').greater_equal(start_dt)
        q.chain('and').on_attribute('end').less_equal(end_dt)

        # Fetch events (limit to reasonable number)
        existing_events = schedule.get_events(query=q, limit=5)

        subject = event_data.get('course', 'No Title')

        for existing_event in existing_events:
            # Check if subject matches
            if existing_event.subject == subject:
                logging.info(f"  - Event '{subject}' already exists. Skipping.")
                return True

        # Create new event
        new_event = schedule.new_event()

        new_event.subject = subject
        new_event.location = event_data.get('room', '')

        # Build body
        body_parts = [
            f"<p><strong>Professor:</strong> {event_data.get('professor', 'N/A')}</p>",
            f"<p><strong>Group:</strong> {event_data.get('group', 'N/A')}</p>",
            f"<p><strong>Mode:</strong> {event_data.get('mode', 'N/A')}</p>"
        ]

        if 'teams_links' in event_data and event_data['teams_links']:
            body_parts.append("<p><strong>Teams Links:</strong></p><ul>")
            for link in event_data['teams_links']:
                link_type = link.get('type', 'Unknown').replace('MTeams_', '')
                url = link.get('url', '')
                body_parts.append(f"<li><a href='{url}'>{link_type}</a></li>")
            body_parts.append("</ul>")

        new_event.body = "".join(body_parts)
        # Explicitly set body type to HTML
        new_event.body_type = 'HTML'

        new_event.start = start_dt
        new_event.end = end_dt

        if new_event.save():
            return True
        else:
            return False

    except Exception as e:
        logging.error(f"Error creating Outlook event '{event_data.get('course', 'Unknown')}': {e}")
        return False

def sync_events_to_calendar(events_file='data/events.json', event_date=None):
    """
    Sync all events from JSON file to Outlook Calendar.

    Args:
        events_file: Path to JSON file with events
        event_date: Date string for events (e.g., "11/17/2025")

    Returns:
        Number of events successfully created
    """
    logging.info("Authenticating with Outlook Calendar...")
    account = authenticate_outlook_calendar()

    if not account:
        logging.error("Failed to authenticate with Outlook Calendar")
        return 0

    schedule = account.schedule()

    # Load events
    logging.info(f"Loading events from {events_file}...")
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        logging.error(f"Events file {events_file} not found.")
        return 0

    logging.info(f"Found {len(events)} events to sync to Outlook")

    # Check if events have individual dates
    events_with_dates = [e for e in events if 'date' in e]

    if events_with_dates:
        logging.info(f"Events span multiple dates - using individual event dates")
    elif not event_date:
        logging.error("Events do not have individual dates and no date was provided")
        return 0

    created_count = 0
    failed_count = 0

    for i, event in enumerate(events, 1):
        date_to_use = event.get('date', event_date)

        if not date_to_use:
            logging.warning(f"Skipping event {i}/{len(events)}: {event.get('course', 'Unknown')} (no date)")
            failed_count += 1
            continue

        logging.debug(f"Creating Outlook event {i}/{len(events)}: {event.get('course', 'Unknown')} on {date_to_use}")

        if create_calendar_event(schedule, event, date_to_use):
            logging.info(f"✓ Created in Outlook: {event.get('course', 'Unknown')} on {date_to_use}")
            created_count += 1
        else:
            logging.error(f"✗ Failed in Outlook: {event.get('course', 'Unknown')} on {date_to_use}")
            failed_count += 1

    logging.info(f"Outlook sync completed: {created_count}/{len(events)} events created ({failed_count} failed)")
    return created_count

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        date_arg = sys.argv[1]
    else:
        date_arg = None
    sync_events_to_calendar(event_date=date_arg)
