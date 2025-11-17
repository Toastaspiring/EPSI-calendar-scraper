# ✅ Google Calendar Setup Checklist

Use this checklist to set up Google Calendar integration. Check off each step as you go!

---

## Prerequisites (Already Done! ✅)

- [x] Python installed
- [x] Virtual environment set up
- [x] Basic scraping working
- [x] Google Calendar packages installed
- [x] 13 events ready to sync

---

## Step 1: Google Cloud Console Setup (5 minutes)

### 1.1 Create Project
- [ ] Go to: https://console.cloud.google.com/
- [ ] Click project dropdown at top
- [ ] Click "New Project"
- [ ] Name: "Schedule Scraper" (or anything)
- [ ] Click "Create"
- [ ] Wait for project creation

### 1.2 Enable Calendar API
- [ ] Click "APIs & Services" in left menu
- [ ] Click "Library"
- [ ] Search for "Google Calendar API"
- [ ] Click on it
- [ ] Click "Enable"
- [ ] Wait for API to enable

### 1.3 Configure OAuth Consent
- [ ] Go to "APIs & Services" → "OAuth consent screen"
- [ ] Select "External" user type
- [ ] Click "Create"
- [ ] Fill in:
  - [ ] App name: "Schedule Scraper"
  - [ ] User support email: (your email)
  - [ ] Developer contact: (your email)
- [ ] Click "Save and Continue"
- [ ] Skip "Scopes" (click "Save and Continue")
- [ ] Add Test Users:
  - [ ] Click "Add Users"
  - [ ] Enter your email
  - [ ] Click "Add"
- [ ] Click "Save and Continue"
- [ ] Review summary, click "Back to Dashboard"

### 1.4 Create OAuth Credentials
- [ ] Go to "APIs & Services" → "Credentials"
- [ ] Click "Create Credentials" → "OAuth client ID"
- [ ] Application type: Select "Desktop app"
- [ ] Name: "Schedule Scraper Desktop"
- [ ] Click "Create"
- [ ] Click "Download JSON" button
- [ ] Save file to your project folder
- [ ] Rename file to exactly: `credentials.json`
- [ ] Verify location:
  ```
  C:\Users\louis\PycharmProjects\PythonProject2\credentials.json
  ```

---

## Step 2: First Authentication (2 minutes)

### 2.1 Run Test
- [ ] Open PowerShell in project folder
- [ ] Run: `python test_setup.py`
- [ ] Verify all tests pass (should now include credentials)

### 2.2 Run Main Script
- [ ] Run: `python main.py`
- [ ] Wait for scraping to complete
- [ ] When prompted "Sync to Google Calendar?":
  - [ ] Type: `y`
  - [ ] Press Enter

### 2.3 Enter Date
- [ ] When prompted for date:
  - [ ] Type: `11/17/2025`
  - [ ] Press Enter

### 2.4 Authorize in Browser
- [ ] Browser should open automatically
- [ ] If warning "Google hasn't verified this app":
  - [ ] Click "Advanced"
  - [ ] Click "Go to Schedule Scraper (unsafe)"
- [ ] Select your Google account
- [ ] Click "Allow" to grant permissions
- [ ] Wait for "authentication flow has completed"
- [ ] Close browser tab
- [ ] Return to terminal

### 2.5 Verify Success
- [ ] Terminal should show:
  ```
  Creating event 1/13: ... ✓
  Creating event 2/13: ... ✓
  ...
  Successfully created 13/13 events
  ```

---

## Step 3: Verify in Google Calendar (1 minute)

- [ ] Open: https://calendar.google.com/
- [ ] Check for your events
- [ ] Click on an event to verify:
  - [ ] Course name as title
  - [ ] Room in location
  - [ ] Professor in description
  - [ ] Time is correct
  - [ ] Reminders set (30 min, 10 min)

---

## Step 4: Test on Mobile (Optional)

- [ ] Install Google Calendar app on phone
- [ ] Sign in with same Google account
- [ ] Check events appear
- [ ] Test a reminder

---

## Troubleshooting

If something doesn't work, check these:

### credentials.json not found
- [ ] File is in correct location
- [ ] File named exactly `credentials.json`
- [ ] File downloaded from correct project

### Browser doesn't open
- [ ] Copy URL from terminal
- [ ] Paste in browser manually
- [ ] Continue with authorization

### "Access blocked" error
- [ ] Added yourself as test user
- [ ] OAuth consent screen configured
- [ ] Correct OAuth client type (Desktop)

### Events not appearing
- [ ] Check correct date entered
- [ ] Verify format: MM/DD/YYYY
- [ ] Check terminal for success messages
- [ ] Try refreshing Google Calendar

### "API not enabled"
- [ ] Go back to Step 1.2
- [ ] Verify Calendar API is enabled
- [ ] Wait a few minutes, try again

---

## Files Checklist

After setup, you should have:

- [x] `main.py`
- [x] `google_calendar_sync.py`
- [x] `cookie`
- [x] `events.json`
- [ ] `credentials.json` (you create this)
- [ ] `token.pickle` (auto-created on auth)

---

## Success Indicators

You'll know it worked when:

- [ ] Terminal shows "Successfully created 13/13 events"
- [ ] Google Calendar web shows your events
- [ ] Events have all details (prof, room, time)
- [ ] Reminders are set
- [ ] Events sync to mobile

---

## Next Time

After first setup, just:

1. [ ] Update `cookie` if expired (from browser)
2. [ ] Run: `python main.py`
3. [ ] Type `y` for sync
4. [ ] Enter new date
5. [ ] Done! (no browser auth needed)

---

## Quick Commands

```powershell
# Test setup
python test_setup.py

# Run scraper + sync
python main.py

# Sync existing events
python google_calendar_sync.py 11/17/2025
```

---

## Help Resources

- **Quick start:** Read `QUICKSTART.md`
- **Detailed guide:** Read `GOOGLE_CALENDAR_SETUP.md`
- **Full docs:** Read `README.md`
- **Questions?** Check `COMPLETION_SUMMARY.md`

---

## ✅ Completion

Once all checkboxes are marked, you're done! 🎉

Your schedule now syncs automatically to Google Calendar!

---

**Total time:** ~10 minutes (one-time setup)
**Next runs:** ~1 minute (just run the script)

