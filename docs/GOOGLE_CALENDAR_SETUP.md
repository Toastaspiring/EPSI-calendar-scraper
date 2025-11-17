# Google Calendar Integration Setup Guide

This guide will walk you through setting up Google Calendar integration step-by-step.

## Prerequisites

- Python 3.7 or higher
- A Google account
- Active internet connection

## Step 1: Install Dependencies

Open PowerShell in the project directory and run:

```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Or install all dependencies at once:

```powershell
pip install -r requirements.txt
```

## Step 2: Create Google Cloud Project

### 2.1 Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Sign in with your Google account

### 2.2 Create a New Project
1. Click the project dropdown at the top
2. Click "New Project"
3. Name it something like "Schedule Scraper"
4. Click "Create"

### 2.3 Enable Google Calendar API
1. In the left sidebar, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it
4. Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

### 3.1 Configure OAuth Consent Screen
1. Go to "APIs & Services" → "OAuth consent screen"
2. Select "External" user type
3. Click "Create"
4. Fill in required fields:
   - App name: "Schedule Scraper"
   - User support email: Your email
   - Developer contact: Your email
5. Click "Save and Continue"
6. Skip "Scopes" (click "Save and Continue")
7. Add yourself as a test user
8. Click "Save and Continue"

### 3.2 Create Credentials
1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. Application type: "Desktop app"
4. Name: "Schedule Scraper Desktop"
5. Click "Create"
6. Click "Download JSON" on the popup
7. **IMPORTANT**: Save the file as `credentials.json` in your project folder:
   ```
   C:\Users\louis\PycharmProjects\PythonProject2\credentials.json
   ```

## Step 4: First-Time Authentication

### 4.1 Run the Script
```powershell
python main.py
```

### 4.2 When Prompted
1. Type `y` when asked to sync to Google Calendar
2. Enter the date (e.g., `11/17/2025`)
3. A browser window will open automatically

### 4.3 Grant Permissions
1. Select your Google account
2. You may see a warning "Google hasn't verified this app"
   - Click "Advanced"
   - Click "Go to Schedule Scraper (unsafe)"
3. Click "Allow" to grant calendar permissions
4. The browser will show "The authentication flow has completed"
5. Return to the terminal

### 4.4 Token Saved
- A `token.pickle` file is created
- Future runs won't require browser authentication

## Step 5: Verify Events in Google Calendar

1. Open Google Calendar: https://calendar.google.com/
2. You should see your schedule events added
3. Events include:
   - Course name as title
   - Room as location
   - Professor and details in description
   - Teams links (if available)
   - Colored by event type
   - Reminders set for 30 and 10 minutes before

## Usage Options

### Option 1: Interactive (with scraping)
```powershell
python main.py
```
- Scrapes schedule
- Prompts for Google Calendar sync
- Enter date when asked

### Option 2: Direct Sync (from existing events.json)
```powershell
python google_calendar_sync.py 11/17/2025
```
- Syncs existing events.json
- Specify date as argument

### Option 3: Custom Date
```powershell
python google_calendar_sync.py 12/01/2025
```

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the OAuth credentials
- File must be named exactly `credentials.json`
- Must be in the same folder as your Python scripts

### "The authentication flow has failed"
- Make sure you added yourself as a test user
- Try deleting `token.pickle` and authenticating again
- Check that Google Calendar API is enabled

### "Access blocked: This app's request is invalid"
- OAuth consent screen not configured correctly
- Go back to Step 3.1 and complete all fields

### Events not showing in calendar
- Check that you entered the correct date
- Verify date format: MM/DD/YYYY
- Check if events were created in the terminal output

### Browser doesn't open automatically
- Copy the URL from terminal and paste in browser manually
- Make sure no firewall is blocking port 8080

## Files Created

After setup, you'll have:
- `credentials.json` - OAuth credentials (you download this)
- `token.pickle` - Authentication token (created automatically)
- `events.json` - Scraped events
- `raw` - Raw HTML from schedule page

## Security Notes

- **credentials.json** contains your OAuth client ID and secret
- **token.pickle** contains your access token
- Keep both files private
- Add them to `.gitignore` if using Git:
  ```
  credentials.json
  token.pickle
  cookie
  ```

## Next Steps

Once set up, you can:
1. Run the script regularly to update your calendar
2. Modify `google_calendar_sync.py` to customize event formatting
3. Add recurring event support
4. Create calendar event reminders
5. Sync to a specific calendar (not just primary)

## Support

If you encounter issues:
1. Check the Google Cloud Console for API quota
2. Verify your credentials are valid
3. Try deleting `token.pickle` and re-authenticating
4. Check Google Calendar API status: https://status.cloud.google.com/

