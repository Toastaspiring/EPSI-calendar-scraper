"""
Google Calendar Integration for Schedule Scraper

This module handles authentication and syncing of events to Google Calendar.
"""

import json
import os
import base64
from datetime import datetime, timezone
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
import logging

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def authenticate_google_calendar():
    """
    Authenticate with Google Calendar API.

    Returns:
        Google Calendar service object
    """
    creds = None

    # Check for environment variables and create files if they don't exist
    if not os.path.exists('token.pickle') and os.environ.get('GOOGLE_TOKEN_PICKLE_BASE64'):
        try:
            token_data = base64.b64decode(os.environ['GOOGLE_TOKEN_PICKLE_BASE64'])
            with open('token.pickle', 'wb') as token:
                token.write(token_data)
            logging.info("Restored token.pickle from environment variable")
        except Exception as e:
            logging.error(f"Failed to decode GOOGLE_TOKEN_PICKLE_BASE64: {e}")

    if not os.path.exists('credentials.json') and os.environ.get('GOOGLE_CREDENTIALS_JSON_BASE64'):
        try:
            creds_data = base64.b64decode(os.environ['GOOGLE_CREDENTIALS_JSON_BASE64'])
            with open('credentials.json', 'wb') as f:
                f.write(creds_data)
            logging.info("Restored credentials.json from environment variable")
        except Exception as e:
            logging.error(f"Failed to decode GOOGLE_CREDENTIALS_JSON_BASE64: {e}")

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        except Exception as e:
            logging.error(f"Error loading token.pickle: {e}")
            # If token is corrupted, we might want to delete it or just ignore it
            creds = None

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                logging.error("credentials.json not found!")
                logging.error("To set up Google Calendar integration:")
                logging.error("1. Go to https://console.cloud.google.com/")
                logging.error("2. Create a new project or select existing one")
                logging.error("3. Enable Google Calendar API")
                logging.error("4. Create OAuth 2.0 credentials (Desktop app)")
                logging.error("5. Download the credentials and save as 'credentials.json'")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def parse_event_datetime(date_str, time_str):
    """
    Parse date and time strings into datetime objects.

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


def create_calendar_event(service, event_data, event_date):
    """
    Create a single event in Google Calendar.

    Args:
        service: Google Calendar service object
        event_data: Dictionary containing event information
        event_date: Date string for the event (e.g., "11/17/2025")

    Returns:
        Created event object or None if failed
    """
    try:
        # Parse datetime
        start_dt, end_dt = parse_event_datetime(event_date, event_data['time'])

        # Build event description
        description_parts = [
            f"Professor: {event_data.get('professor', 'N/A')}",
            f"Group: {event_data.get('group', 'N/A')}",
            f"Mode: {event_data.get('mode', 'N/A')}"
        ]

        if 'teams_links' in event_data and event_data['teams_links']:
            description_parts.append("\nTeams Links:")
            for link in event_data['teams_links']:
                link_type = link.get('type', 'Unknown').replace('MTeams_', '')
                description_parts.append(f"- {link_type}: {link.get('url', '')}")

        description = '\n'.join(description_parts)

        # Create event
        event = {
            'summary': event_data.get('course', 'No Title'),
            'location': event_data.get('room', ''),
            'description': description,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'Europe/Paris',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'Europe/Paris',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        # Add color based on event color
        color_mapping = {
            '#FFDDFF': '1',  # Lavender
            '#DDEEDD': '2',  # Sage
            '#DDDDFF': '3',  # Grape
            '#DDFFDD': '10', # Basil
            '#EEDDEE': '4',  # Flamingo
            '#DDDDEE': '3',  # Grape
            '#EEEEEE': '8',  # Graphite
        }

        if 'color' in event_data:
            event['colorId'] = color_mapping.get(event_data['color'], '9')

        # Insert event into primary calendar
        created_event = service.events().insert(calendarId='primary', body=event).execute()

        return created_event

    except Exception as e:
        logging.error(f"Error creating event '{event_data.get('course', 'Unknown')}': {e}")
        return None


def sync_events_to_calendar(events_file='data/events.json', event_date=None):
    """
    Sync all events from JSON file to Google Calendar.

    Args:
        events_file: Path to JSON file with events
        event_date: Date string for events (e.g., "11/17/2025")
                   If None, each event's individual date will be used

    Returns:
        Number of events successfully created
    """
    # Authenticate
    logging.info("Authenticating with Google Calendar...")
    service = authenticate_google_calendar()

    if not service:
        logging.error("Failed to authenticate with Google Calendar")
        return 0

    # Load events
    logging.info(f"Loading events from {events_file}...")
    with open(events_file, 'r', encoding='utf-8') as f:
        events = json.load(f)

    logging.info(f"Found {len(events)} events to sync")

    # Check if events have individual dates
    events_with_dates = [e for e in events if 'date' in e]

    if events_with_dates:
        logging.info(f"Events span multiple dates - using individual event dates")
    elif not event_date:
        # For cron jobs, if no date is provided and events don't have dates, fail
        logging.error("Events do not have individual dates and no date was provided")
        return 0

    # Create events
    logging.info(f"Creating events in Google Calendar...")
    created_count = 0
    failed_count = 0

    for i, event in enumerate(events, 1):
        # Use event's date if available, otherwise use the provided date
        date_to_use = event.get('date', event_date)

        if not date_to_use:
            logging.warning(f"Skipping event {i}/{len(events)}: {event.get('course', 'Unknown')} (no date)")
            failed_count += 1
            continue

        logging.debug(f"Creating event {i}/{len(events)}: {event.get('course', 'Unknown')} on {date_to_use}")

        created = create_calendar_event(service, event, date_to_use)

        if created:
            logging.info(f"✓ Created: {event.get('course', 'Unknown')} on {date_to_use}")
            created_count += 1
        else:
            logging.error(f"✗ Failed: {event.get('course', 'Unknown')} on {date_to_use}")
            failed_count += 1

    logging.info(f"Successfully created {created_count}/{len(events)} events ({failed_count} failed)")

    return created_count


def list_upcoming_events(service, max_results=10):
    """
    List upcoming events from Google Calendar.

    Args:
        service: Google Calendar service object
        max_results: Maximum number of events to return
    """
    now = datetime.now(timezone.utc).isoformat()

    logging.info(f'Getting the upcoming {max_results} events...')
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        logging.info('No upcoming events found.')
        return

    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        logging.info(f"- {start}: {event['summary']}")


if __name__ == '__main__':
    # Example usage
    import sys

    if len(sys.argv) > 1:
        date_arg = sys.argv[1]
    else:
        date_arg = None

    sync_events_to_calendar(event_date=date_arg)

