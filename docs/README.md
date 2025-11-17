# Schedule Scraper

This script scrapes your schedule from the WigorServices EDT (timetable) system and extracts all calendar events.

## Features

- **Fetch schedule page**: Uses cookies authentication to fetch your personalized schedule
- **Extract events**: Parses HTML to extract all calendar events with details
- **Export to JSON**: Saves events to a structured JSON file for easy processing
- **Pretty print**: Displays events in a readable format in the console

## Files

- `main.py`: Main script with all functionality
- `cookie`: File containing your authentication cookies
- `raw`: Raw HTML of the fetched schedule page
- `events.json`: Extracted events in JSON format

## Usage

### Basic Usage

```bash
python main.py
```

This will:
1. Fetch the schedule page using cookies from the `cookie` file
2. Extract all events from the page
3. Print events to console
4. Save events to `events.json`

### Updating Cookies

If you get a login page instead of your schedule, your cookies have expired. To update them:

1. Open the schedule URL in your browser and log in
2. Open DevTools (F12) → Network tab
3. Refresh the page
4. Find the request to `WebPsDyn.aspx?Action=posEDTLMS`
5. Copy the `Cookie` header value
6. Update the `cookie` file with the new value

Format: `ASP.NET_SessionId=xxx; .DotNetCasClientAuth=xxx`

## Event Data Structure

Each extracted event contains:

- **course**: Course name/title
- **professor**: Professor name
- **group**: Student group/class
- **time**: Time range (e.g., "09:00 - 12:30")
- **room**: Room location
- **mode**: Attendance mode (e.g., "Présenciel", "Distanciel")
- **color**: Event background color (hex code)
- **teams_links**: List of Microsoft Teams meeting links (if available)

## Functions

### `fetch_page()`
Fetches the schedule page from the server using cookies authentication.

Returns: BeautifulSoup object with parsed HTML

### `extract_events(soup)`
Extracts all calendar events from the parsed HTML.

Parameters:
- `soup`: BeautifulSoup object with parsed HTML

Returns: List of event dictionaries

### `print_events(events)`
Prints events in a readable format to console.

Parameters:
- `events`: List of event dictionaries

### `save_events_to_json(events, filename='events.json')`
Saves events to a JSON file.

Parameters:
- `events`: List of event dictionaries
- `filename`: Output filename (default: events.json)

## Example Output

```json
{
  "course": "Entrepots de données (Datamart)",
  "mode": "Présenciel",
  "professor": "causeur yann",
  "group": "CC MASTERE 1 CYBER +  INFRA + ECDPIA + EID 25/26",
  "time": "13:00 - 15:00",
  "room": "201-EPSI(ST EXUPERY)",
  "color": "#FFDDFF"
}
```

## Google Calendar Integration

### Setup

1. **Install Google Calendar API dependencies**:
   ```bash
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

2. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Calendar API
   - Create OAuth 2.0 credentials (Desktop app type)
   - Download the credentials JSON file
   - Save it as `credentials.json` in the project directory

3. **First-time authentication**:
   - Run the script and choose to sync to Google Calendar
   - A browser window will open for authentication
   - Sign in with your Google account
   - Grant the requested permissions
   - The token will be saved for future use

### Using Google Calendar Sync

#### From main.py (Interactive)
```bash
python main.py
```
When prompted, enter 'y' to sync to Google Calendar, then enter the date.

#### Direct sync from existing events.json
```bash
python google_calendar_sync.py 11/17/2025
```

### What Gets Synced

Each event will include:
- **Title**: Course name
- **Location**: Room information
- **Description**: Professor, group, attendance mode, and Teams links
- **Time**: Start and end times
- **Color**: Events are color-coded by type
- **Reminders**: 30 minutes and 10 minutes before event

### Files Created During Sync

- `credentials.json`: OAuth credentials (you create this)
- `token.pickle`: Authentication token (created automatically)

## GitHub Actions (Automated Cloud Runs)

### Run Automatically Every Monday

The schedule scraper can run automatically in GitHub Actions:

1. **Push code to GitHub**
2. **Add two secrets** (cookie and Google credentials)
3. **Done!** Runs every Monday at 6 AM UTC

**See:** `GITHUB_ACTIONS_SETUP.md` for complete setup guide

**Quick Reference:** `GITHUB_ACTIONS_QUICKREF.md`

### Features
- ✅ Runs in the cloud (no local computer needed)
- ✅ Automatic weekly schedule sync
- ✅ Saves logs and events as artifacts
- ✅ Email notifications on failure
- ✅ Can be manually triggered anytime
- ✅ Free tier includes 2,000 minutes/month

---

## Dependencies

### Basic Scraping
- `requests`: HTTP library for fetching pages
- `beautifulsoup4`: HTML parsing library

Install with:
```bash
pip install requests beautifulsoup4
```

### Google Calendar Integration (Optional)
- `google-auth`: Google authentication
- `google-auth-oauthlib`: OAuth flow
- `google-auth-httplib2`: HTTP transport
- `google-api-python-client`: Google API client

Install with:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Or install all dependencies:
```bash
pip install requests beautifulsoup4 google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Notes

- The URL can be customized in the `fetch_page()` function
- The script automatically handles multiple cookies from the cookie file
- Teams meeting links are preserved if available in the schedule
- The script detects if you're redirected to a login page and warns you

