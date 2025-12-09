import requests
from bs4 import BeautifulSoup
import json
import re
import os
from datetime import datetime
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


def fetch_page():
    # Generate today's date in the format MM/DD/YYYY for the API
    current_date = datetime.now().strftime('%m/%d/%Y')
    url = f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=louis.marec&date={current_date}"
    logging.info(f"Using date: {current_date}")

    # Read cookie from file
    with open('data/cookie', 'r') as f:
        cookie_string = f.read().strip()

    # Parse cookies from the cookie string
    cookies = {}
    for cookie in cookie_string.split('; '):
        if '=' in cookie:
            name, value = cookie.split('=', 1)
            cookies[name] = value

    logging.info(f"Using cookies: {list(cookies.keys())}")

    # Set up headers to match the working browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'sec-ch-ua': '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1'
    }

    # Fetch the page
    logging.info(f"Fetching schedule from: {url}")
    response = requests.get(url, headers=headers, cookies=cookies, allow_redirects=True)
    response.raise_for_status()

    logging.info(f"Final URL: {response.url}")
    logging.info(f"Page fetched successfully. Status code: {response.status_code}")

    # Parse with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Check if we got a login page
    if 'Connexion' in (soup.title.string if soup.title else ''):
        logging.error("Received a login page. Cookies have expired!")
        logging.error("Update the 'cookie' file with fresh credentials from browser")
        raise Exception("Authentication failed - cookies expired")
    else:
        logging.info("Successfully authenticated and got schedule page")

    # Save raw HTML
    os.makedirs('data', exist_ok=True)
    with open('data/raw', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    return soup


def extract_events(soup):
    """
    Extract all calendar events from the parsed HTML.

    Returns:
        List of dictionaries containing event information
    """
    events = []

    # First, extract day headers with their positions to map dates
    day_headers = {}
    jour_divs = soup.find_all('div', class_='Jour')

    french_months = {
        'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
        'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
        'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12
    }

    for jour_div in jour_divs:
        style = jour_div.get('style', '')
        # Extract left position
        left_match = re.search(r'left:([\d.]+)%', style)
        if left_match:
            left_pos = float(left_match.group(1))

            # Extract date from the day header
            tcjour = jour_div.find('td', class_='TCJour')
            if tcjour:
                day_text = tcjour.get_text(strip=True)
                # Parse format like "Lundi 17 Novembre"
                date_match = re.search(r'(\d+)\s+(\w+)', day_text)
                if date_match:
                    day_num = int(date_match.group(1))
                    month_name = date_match.group(2).lower()

                    if month_name in french_months:
                        month_num = french_months[month_name]
                        # Use current year
                        year = datetime.now().year

                        try:
                            date_obj = datetime(year, month_num, day_num)
                            day_headers[left_pos] = date_obj.strftime('%m/%d/%Y')
                        except ValueError:
                            pass

    # Find all event divs with class="Case"
    case_divs = soup.find_all('div', class_='Case')

    for case in case_divs:
        # Skip shadow divs and other non-event Cases
        if 'id' in case.attrs and case['id'] == 'Apres':
            continue

        # Find the table with event details
        table = case.find('table', class_='TCase')
        if not table:
            continue

        event = {}

        # Extract date based on position
        style = case.get('style', '')
        left_match = re.search(r'left:([\d.]+)%', style)
        if left_match:
            event_left = float(left_match.group(1))

            # Find the closest day header position
            closest_day_pos = None
            min_diff = float('inf')
            for day_pos in day_headers.keys():
                diff = abs(event_left - day_pos)
                if diff < min_diff:
                    min_diff = diff
                    closest_day_pos = day_pos

            if closest_day_pos is not None:
                event['date'] = day_headers[closest_day_pos]

        # Extract course name (first TCase td)
        course_cell = table.find('td', class_='TCase')
        if course_cell:
            # Remove Teams div content to get clean course name
            teams_div = course_cell.find('div', class_='Teams')
            if teams_div:
                teams_div.decompose()
            presence_div = course_cell.find('div', class_='Presence')
            if presence_div:
                presence_div.decompose()
            event['course'] = course_cell.get_text(strip=True)

            # Extract Teams links
            teams_div = case.find('div', class_='Teams')
            if teams_div:
                teams_links = []
                for link in teams_div.find_all('a'):
                    teams_links.append({
                        'url': link.get('href', ''),
                        'type': link.find('img').get('src', '').split('/')[-1].replace('.png', '') if link.find('img') else ''
                    })
                event['teams_links'] = teams_links

        # Extract professor and group info
        prof_cell = table.find('td', class_='TCProf')
        if prof_cell:
            # Check for presence/remote mode
            mode_img = prof_cell.find('img')
            if mode_img:
                event['mode'] = mode_img.get('title', mode_img.get('alt', ''))

            text_content = prof_cell.get_text('\n', strip=True).split('\n')
            if len(text_content) > 0:
                event['professor'] = text_content[0]
            if len(text_content) > 1:
                event['group'] = text_content[1]

        # Extract time
        time_cell = table.find('td', class_='TChdeb')
        if time_cell:
            event['time'] = time_cell.get_text(strip=True)

        # Extract room
        room_cell = table.find('td', class_='TCSalle')
        if room_cell:
            event['room'] = room_cell.get_text(strip=True).replace('Salle:', '').strip()

        # Extract background color to determine event type
        if 'background-color:' in style:
            color = style.split('background-color:')[1].split(';')[0].strip()
            event['color'] = color

        # Only add if we have at least a course name
        if 'course' in event:
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
        if 'teams_links' in event:
            logging.debug(f"  Teams Links: {len(event['teams_links'])} available")


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
    parser = argparse.ArgumentParser(description='Scrape schedule and optionally sync to Google Calendar')
    parser.add_argument('--no-sync', action='store_true', help='Skip Google Calendar sync')
    parser.add_argument('--sync-only', action='store_true', help='Only sync existing events.json, skip scraping')
    args = parser.parse_args()

    try:
        if not args.sync_only:
            # Scrape schedule
            logging.info("Starting schedule scraper...")
            soup = fetch_page()
            events = extract_events(soup)
            print_events(events)
            save_events_to_json(events)
            logging.info("Scraping completed successfully")

        # Sync to Google Calendar (unless --no-sync flag is set)
        if not args.no_sync:
            try:
                from scripts.google_calendar_sync import sync_events_to_calendar

                logging.info("Starting Google Calendar sync...")
                # Events now have individual dates, no need to ask
                created_count = sync_events_to_calendar()
                logging.info(f"Google Calendar sync completed: {created_count} events created")
            except ImportError:
                logging.error("Google Calendar module not available.")
                logging.error("Install required packages: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            except Exception as e:
                logging.error(f"Error syncing to Google Calendar: {e}")
                raise
        else:
            logging.info("Skipping Google Calendar sync (--no-sync flag set)")

        logging.info("All operations completed successfully")
        sys.exit(0)

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

