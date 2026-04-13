"""
Google Calendar Integration for Schedule Scraper

This module handles authentication and syncing of events to Google Calendar.
"""

import json
import os
from datetime import datetime, timedelta, timezone
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

    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('data/token.pickle'):
        with open('data/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('data/credentials.json'):
                logging.error("credentials.json not found!")
                logging.error("To set up Google Calendar integration:")
                logging.error("1. Go to https://console.cloud.google.com/")
                logging.error("2. Create a new project or select existing one")
                logging.error("3. Enable Google Calendar API")
                logging.error("4. Create OAuth 2.0 credentials (Desktop app)")
                logging.error("5. Download the credentials and save as 'data/credentials.json'")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('data/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def parse_event_datetime(event_data):
    """
    Parse event datetime from either ISO format (new API) or legacy date+time strings.

    Args:
        event_data: Event dictionary with either:
            - 'start'/'end' ISO 8601 strings (new format)
            - 'date' + 'time' strings (legacy format)

    Returns:
        Tuple of (start_datetime, end_datetime)
    """
    # Try new ISO format first
    if 'start' in event_data and 'end' in event_data:
        try:
            start_dt = datetime.fromisoformat(event_data['start'])
            end_dt = datetime.fromisoformat(event_data['end'])
            # Strip timezone info for Google Calendar (we pass timezone separately)
            return start_dt.replace(tzinfo=None), end_dt.replace(tzinfo=None)
        except (ValueError, TypeError):
            pass

    # Fall back to legacy date + time format
    date_str = event_data.get('date', '')
    time_str = event_data.get('time', '')

    if not date_str or not time_str:
        raise ValueError(f"Event has no parseable date/time: {event_data.get('course', 'Unknown')}")

    start_time, end_time = time_str.split(' - ')
    date_parts = date_str.split('/')
    month, day, year = int(date_parts[0]), int(date_parts[1]), int(date_parts[2])

    start_hour, start_min = map(int, start_time.split(':'))
    start_dt = datetime(year, month, day, start_hour, start_min)

    end_hour, end_min = map(int, end_time.split(':'))
    end_dt = datetime(year, month, day, end_hour, end_min)

    return start_dt, end_dt


def build_event_body(event_data):
    """
    Build a Google Calendar event body from scraped event data.

    Args:
        event_data: Dictionary containing event information

    Returns:
        Tuple of (event_body dict, start_dt, end_dt) or None on failure
    """
    start_dt, end_dt = parse_event_datetime(event_data)

    # Build event description
    description_parts = [
        f"Professor: {event_data.get('professor', 'N/A')}",
        f"Group: {event_data.get('group', 'N/A')}",
        f"Mode: {event_data.get('mode', 'N/A')}"
    ]
    description = '\n'.join(description_parts)

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

    return event, start_dt, end_dt


def fetch_existing_events(service, time_min, time_max):
    """
    Fetch all existing events from Google Calendar in the given time range.

    Returns:
        Dict mapping (summary, start_iso) -> event object
    """
    time_min_iso = time_min.isoformat() + '+02:00'
    time_max_iso = time_max.isoformat() + '+02:00'

    logging.info(f"Fetching existing calendar events from {time_min_iso} to {time_max_iso}")

    existing = {}
    page_token = None

    while True:
        result = service.events().list(
            calendarId='primary',
            timeMin=time_min_iso,
            timeMax=time_max_iso,
            singleEvents=True,
            orderBy='startTime',
            maxResults=250,
            pageToken=page_token,
        ).execute()

        for ev in result.get('items', []):
            summary = ev.get('summary', '')
            start = ev['start'].get('dateTime', ev['start'].get('date', ''))
            key = (summary, start)
            existing[key] = ev

        page_token = result.get('nextPageToken')
        if not page_token:
            break

    logging.info(f"Found {len(existing)} existing events in range")
    return existing


def event_needs_update(existing_event, new_body):
    """
    Check if an existing Google Calendar event differs from the new data.

    Compares: location (room), description (professor/group/mode).
    """
    if existing_event.get('location', '') != new_body.get('location', ''):
        return True
    if existing_event.get('description', '') != new_body.get('description', ''):
        return True
    # Check if end time changed
    existing_end = existing_event.get('end', {}).get('dateTime', '')
    new_end = new_body.get('end', {}).get('dateTime', '')
    if existing_end and new_end:
        # Normalize for comparison (strip timezone offset differences)
        try:
            if datetime.fromisoformat(existing_end) != datetime.fromisoformat(new_end + '+02:00' if '+' not in new_end else new_end):
                return True
        except (ValueError, TypeError):
            pass
    return False


def sync_events_to_calendar(events_file='data/events.json'):
    """
    Sync all events from JSON file to Google Calendar using upsert logic.

    - If event does not exist: create it
    - If event exists but data changed: update it
    - If event exists and is identical: skip it

    Events are matched by (summary, start_datetime).

    Args:
        events_file: Path to JSON file with events

    Returns:
        Number of events created or updated
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

    # Parse all events and compute the time range
    parsed_events = []
    for event_data in events:
        has_dates = ('start' in event_data and 'end' in event_data) or ('date' in event_data and 'time' in event_data)
        if not has_dates:
            continue
        try:
            body, start_dt, end_dt = build_event_body(event_data)
            parsed_events.append((event_data, body, start_dt, end_dt))
        except Exception as e:
            logging.warning(f"Skipping unparseable event: {event_data.get('course', '?')}: {e}")

    if not parsed_events:
        logging.warning("No valid events to sync")
        return 0

    # Compute time range for fetching existing events (with 1h buffer)
    all_starts = [s for _, _, s, _ in parsed_events]
    all_ends = [e for _, _, _, e in parsed_events]
    range_min = min(all_starts) - timedelta(hours=1)
    range_max = max(all_ends) + timedelta(hours=1)

    # Fetch existing events in that range
    existing = fetch_existing_events(service, range_min, range_max)

    # Upsert loop
    created_count = 0
    updated_count = 0
    skipped_count = 0
    failed_count = 0

    for event_data, body, start_dt, end_dt in parsed_events:
        course = event_data.get('course', 'Unknown')
        # Build the lookup key matching what Google Calendar returns
        start_iso = start_dt.isoformat() + '+02:00'
        key = (body['summary'], start_iso)

        try:
            if key in existing:
                # Event exists - check if it needs updating
                existing_event = existing[key]
                if event_needs_update(existing_event, body):
                    service.events().update(
                        calendarId='primary',
                        eventId=existing_event['id'],
                        body=body,
                    ).execute()
                    logging.info(f"Updated: {course} on {start_dt.strftime('%m/%d')}")
                    updated_count += 1
                else:
                    logging.info(f"Skipped (unchanged): {course} on {start_dt.strftime('%m/%d')}")
                    skipped_count += 1
            else:
                # Event does not exist - create it
                service.events().insert(calendarId='primary', body=body).execute()
                logging.info(f"Created: {course} on {start_dt.strftime('%m/%d')}")
                created_count += 1
        except Exception as e:
            logging.error(f"Failed: {course} on {start_dt.strftime('%m/%d')}: {e}")
            failed_count += 1

    logging.info(
        f"Sync complete: {created_count} created, {updated_count} updated, "
        f"{skipped_count} unchanged, {failed_count} failed"
    )
    return created_count + updated_count


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
    sync_events_to_calendar()

