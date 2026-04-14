"""
Outlook Calendar Integration for Schedule Scraper

This module handles authentication and syncing of events to Microsoft Outlook Calendar
using the Microsoft Graph API via the O365 library.
"""

import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional

try:
    from O365 import Account, FileSystemTokenBackend
except ImportError:
    logging.error("O365 module not found. Install it with: pip install O365")
    sys.exit(1)


# Scopes required for Calendar access
SCOPES = ['Calendars.ReadWrite']


def authenticate_outlook() -> Optional[Account]:
    """
    Authenticate with Microsoft Graph API.
    
    Expects MS_CLIENT_ID and MS_CLIENT_SECRET environment variables.
    
    Returns:
        O365 Account object or None if authentication fails
    """
    client_id = os.environ.get('MS_CLIENT_ID')
    client_secret = os.environ.get('MS_CLIENT_SECRET')

    if not client_id or not client_secret:
        logging.error("Missing Outlook credentials.")
        logging.error("Please set MS_CLIENT_ID and MS_CLIENT_SECRET environment variables")
        return None

    # Ensure data directory exists for token storage
    os.makedirs('data', exist_ok=True)
    
    # Token persistence
    token_backend = FileSystemTokenBackend(token_path='data', token_filename='o365_token.txt')
    
    credentials = (client_id, client_secret)
    account = Account(credentials, token_backend=token_backend)

    if not account.is_authenticated:
        # If running in CI (headless), we need to inject the token or fail
        ms_token_base64 = os.environ.get('MS_TOKEN_BASE64')
        
        if ms_token_base64 and not os.path.exists('data/o365_token.txt'):
            try:
                import base64
                logging.info("Restoring Outlook token from secret...")
                decoded = base64.b64decode(ms_token_base64)
                with open('data/o365_token.txt', 'wb') as f:
                    f.write(decoded)
                # Re-init account with new token file
                account = Account(credentials, token_backend=token_backend)
            except Exception as e:
                logging.error(f"Failed to restore token from secret: {e}")

        # If still not authenticated and not headless, try interactive
        if not account.is_authenticated:
            # Check if we are interactive
            if sys.stdin and sys.stdin.isatty():
                logging.info("Authentication required. Opening confirmation link...")
                account.authenticate(scopes=SCOPES)
            else:
                logging.error("Authentication required but running in headless mode (no token found).")
                logging.error("Please run locally first to generate 'data/o365_token.txt'")
                return None

    return account


def parse_event_datetime(event_data: Dict[str, Any]):
    """
    Parse event datetime from either ISO format (new API) or legacy date+time strings.

    Returns:
        Tuple of (start_datetime, end_datetime) or (None, None) on failure
    """
    # Try new ISO format first
    if 'start' in event_data and 'end' in event_data:
        try:
            start_dt = datetime.fromisoformat(event_data['start'])
            end_dt = datetime.fromisoformat(event_data['end'])
            # Wigor's Kendo scheduler is configured with timezone "Etc/UTC",
            # so its displayed wall-time is the UTC value. Convert to UTC
            # then drop tzinfo so the value we sync matches what Wigor shows.
            if start_dt.tzinfo is not None:
                start_dt = start_dt.astimezone(timezone.utc).replace(tzinfo=None)
            if end_dt.tzinfo is not None:
                end_dt = end_dt.astimezone(timezone.utc).replace(tzinfo=None)
            return start_dt, end_dt
        except (ValueError, TypeError):
            pass

    # Fall back to legacy date + time format
    date_str = event_data.get('date', '')
    time_str = event_data.get('time', '')

    if not date_str or not time_str:
        return None, None

    try:
        start_time, end_time = time_str.split(' - ')
        parts = date_str.split('/')
        if len(parts) == 3:
            month, day, year = map(int, parts)
        else:
            return None, None

        start_h, start_m = map(int, start_time.split(':'))
        end_h, end_m = map(int, end_time.split(':'))

        start_dt = datetime(year, month, day, start_h, start_m)
        end_dt = datetime(year, month, day, end_h, end_m)
        return start_dt, end_dt
    except (ValueError, TypeError):
        return None, None


def sync_events_to_outlook(events: List[Dict[str, Any]]) -> int:
    """
    Sync events to Outlook Calendar.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        Count of created events
    """
    account = authenticate_outlook()
    if not account:
        return 0

    schedule = account.schedule()
    calendar = schedule.get_default_calendar()
    
    if not calendar:
        logging.error("Could not access default calendar")
        return 0

    logging.info(f"Syncing {len(events)} events to Outlook Calendar...")
    created_count = 0
    
    for event_data in events:
        try:
            start_dt, end_dt = parse_event_datetime(event_data)
            if not start_dt or not end_dt:
                logging.warning(f"Skipping event with no date: {event_data.get('course', 'Unknown')}")
                continue

            # Check duplication (naive check by subject + start time)
            # O365 library query filter
            query = calendar.new_query('start').greater_equal(start_dt)
            query.chain('and').on_attribute('subject').equals(event_data.get('course'))
            existing = calendar.get_events(query=query, include_recurring=False)
            
            # Filter results manually to be precise on start time
            is_duplicate = False
            for e in existing:
                if e.start == start_dt:  # O365 internal datetime comparison
                    is_duplicate = True
                    break
            
            if is_duplicate:
                logging.debug(f"Skipping duplicate: {event_data.get('course')} on {date_str}")
                continue

            # Create new event
            new_event = calendar.new_event()
            new_event.subject = event_data.get('course', 'No Title')
            new_event.location = event_data.get('room', '')
            
            # Build Body
            body_parts = [
                f"<b>Professor:</b> {event_data.get('professor', 'N/A')}",
                f"<b>Group:</b> {event_data.get('group', 'N/A')}",
                f"<b>Mode:</b> {event_data.get('mode', 'N/A')}"
            ]
            
            if event_data.get('teams_links'):
                body_parts.append("<br><b>Teams Links:</b><ul>")
                for link in event_data['teams_links']:
                    link_type = link.get('type', 'Unknown').replace('MTeams_', '')
                    url = link.get('url', '#')
                    body_parts.append(f"<li><a href='{url}'>{link_type}</a></li>")
                body_parts.append("</ul>")

            new_event.body = "<br>".join(body_parts)
            new_event.start = start_dt
            new_event.end = end_dt
            
            # Save
            if new_event.save():
                logging.info(f"✓ Created: {event_data.get('course')} on {date_str}")
                created_count += 1
            else:
                logging.error(f"✗ Failed to save: {event_data.get('course')}")

        except Exception as e:
            logging.error(f"Error syncing event: {e}")

    logging.info(f"Outlook Sync complete: {created_count} events created")
    return created_count
