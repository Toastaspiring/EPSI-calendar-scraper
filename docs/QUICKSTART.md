# Quick Start Guide - Google Calendar Integration

## TL;DR - Get Started in 5 Minutes

### 1. Install Dependencies
```powershell
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Get Google Calendar Credentials

**Fast Track:**
1. Go to: https://console.cloud.google.com/
2. Create new project
3. Enable "Google Calendar API"
4. Create OAuth credentials (Desktop app)
5. Download as `credentials.json` → save in project folder

**Detailed Guide:** See `GOOGLE_CALENDAR_SETUP.md`

### 3. Run the Script
```powershell
python main.py
```

When prompted:
- Type `y` to sync to Google Calendar
- Enter date (e.g., `11/17/2025`)
- Authorize in browser (first time only)

### 4. Check Your Calendar
Open https://calendar.google.com/ - your events should be there!

---

## What You'll See

The script will:
1. ✓ Scrape your schedule
2. ✓ Extract 13+ events
3. ✓ Ask if you want to sync
4. ✓ Open browser for Google auth (first time)
5. ✓ Create events in your calendar
6. ✓ Show success message

---

## Alternative: Sync Only (No Scraping)

If you already have `events.json`:

```powershell
python google_calendar_sync.py 11/17/2025
```

---

## Troubleshooting

### "credentials.json not found"
→ You need to create OAuth credentials first
→ See `GOOGLE_CALENDAR_SETUP.md` Step 2-3

### Browser doesn't open
→ Copy URL from terminal and paste in browser

### "Access blocked"
→ Add yourself as test user in OAuth consent screen

---

## Next Time

After first setup, just run:
```powershell
python main.py
```

No browser popup needed - it remembers your authentication!

---

## What Gets Added to Calendar

Each event includes:
- 📚 **Course name** as title
- 📍 **Room** as location
- 👨‍🏫 **Professor** in description
- ⏰ **Exact times**
- 🔔 **Reminders** (30 min & 10 min before)
- 🎨 **Color coding** by type
- 🔗 **Teams links** (if available)

---

## Files You Need

| File | What is it | Where to get it |
|------|-----------|-----------------|
| `credentials.json` | OAuth credentials | Download from Google Cloud Console |
| `cookie` | Schedule auth cookies | Copy from browser (already have) |
| `token.pickle` | Google auth token | Created automatically on first run |

---

## Quick Commands

```powershell
# Full workflow (scrape + sync)
python main.py

# Sync existing events
python google_calendar_sync.py 11/17/2025

# Just scrape (no calendar)
python main.py
# (Press 'n' when asked about Google Calendar)

# Install everything
pip install -r requirements.txt
```

---

## Common Workflow

**Weekly schedule update:**
```powershell
# Update cookie in browser first if expired
python main.py
# Type 'y' for calendar sync
# Enter this week's date
```

**Done!** Check Google Calendar app on phone/computer.

---

## Need Help?

1. **Detailed setup**: Read `GOOGLE_CALENDAR_SETUP.md`
2. **General usage**: Read `README.md`
3. **Can't find credentials.json**: You need to create it (Step 2 above)

---

## Pro Tips

💡 **Run weekly** to keep calendar updated
💡 **Use same Google account** on phone for mobile sync
💡 **Set up recurring** with Windows Task Scheduler
💡 **Different calendar?** Modify `calendarId` in `google_calendar_sync.py`
💡 **Delete all events?** Use Google Calendar web interface bulk delete

---

## That's It!

You're all set. Your schedule will now automatically sync to Google Calendar! 🎉

