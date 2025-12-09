# WigorServices Schedule Scraper - Documentation

**Complete guide to setting up, running, and integrating with the WigorServices Schedule Scraper.**

---

## 📚 Table of Contents
1. [Project Overview](#-project-overview)
2. [Setup Guide (Local & Google Cloud)](#-setup-guide)
3. [Technical Guide (API & Integration)](#-technical-guide)
4. [Troubleshooting](#-troubleshooting)

---

## 🔭 Project Overview

This tool scrapes your schedule from the WigorServices EDT (timetable) system and extracts all calendar events. It can run locally or automatically in the cloud via GitHub Actions.

### Features
- **Fetch schedule page**: Authenticates via cookies or auto-login.
- **Extract events**: KPI-driven parsing of HTML schedule.
- **Export to JSON**: Structured data for easy processing.
- **Google Calendar Sync**: Automatically pushes events to your calendar.
- **Teams Links**: Preserves Microsoft Teams meeting links.

### Project Structure
```
PythonProject2/
├── main.py                      # Main scraper script
├── scripts/
│   ├── wigor_login.py           # Auto-login & Cookie generation
│   └── google_calendar_sync.py  # Standalone sync script
├── .github/workflows/           # Automation
├── data/                        # JSON & Raw HTML output
├── logs/                        # Execution logs
└── docs/                        # You are here
```

---

## 🛠 Setup Guide

### 1. Prerequisites
- **Python 3.7+**
- **Google Account** (for Calendar sync)
- **Chrome Browser** (for auto-login)

### 2. Installation
```bash
# Clone the repo (if you haven't)
git clone https://github.com/YOUR_USERNAME/schedule-scraper.git
cd schedule-scraper

# Install dependencies
pip install -r requirements.txt
```

### 3. Google Cloud Setup (One-Time)
To enable Google Calendar sync, you need to set up a project in Google Cloud.

1.  **Create Project**: Go to [Google Cloud Console](https://console.cloud.google.com/) -> New Project.
2.  **Enable API**: Search for "Google Calendar API" -> Enable.
3.  **Configure OAuth**:
    *   **Consent Screen**: Select "External", add your email as a "Test User".
    *   **Credentials**: Create Credentials -> OAuth Client ID -> Desktop App.
4.  **Download Credentials**: Download the JSON file, rename it to `credentials.json`, and place it in the project root.

### 4. Running the Scraper
You have two options for authentication: Auto-login (Recommended) or Manual Cookies.

#### Option A: Auto-Login (Recommended)
This script uses Selenium to log in and generate fresh cookies automatically.

```bash
# 1. Generate cookies (Follow prompts)
python scripts/wigor_login.py

# 2. Run the main scraper
python main.py
```

#### Option B: Manual Cookies
If auto-login fails, you can manually get cookies:
1.  Log in to WigorServices in your browser.
2.  Open DevTools (F12) -> Network Tab.
3.  Refresh the page. Find the request to `WebPsDyn.aspx`.
4.  Copy the `Cookie` header value.
5.  Create a file named `cookie` (no extension) in project root and paste the value.
    *   Format: `ASP.NET_SessionId=...; .DotNetCasClientAuth=...`

---

## ⚙ Technical Guide

### API Documentation
The scraper interacts with WigorServices via HTTP requests mimicking a browser.

#### Endpoints
*   **Login**: `https://cas-p.wigorservices.net/cas/login`
*   **Schedule**: `https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date={date}`

#### Event Data Structure (`events.json`)
```json
{
  "date": "11/17/2025",
  "course": "Data Management",
  "professor": "Causeur Yann",
  "group": "MASTERE 1 CYBER",
  "time": "13:30 - 17:30",
  "room": "201-EPSI",
  "mode": "Présenciel",
  "teams_links": [
    {"url": "https://teams.microsoft.com/...", "type": "PRINCIPAL"}
  ]
}
```

### Custom Integration
You can import the logic into your own scripts:

```python
from scripts.wigor_login import setup_driver, perform_login
# ... (See scripts/wigor_login.py for full code)
```

---

## ❓ Troubleshooting

### Common Issues

#### `credentials.json` not found
*   **Cause**: You didn't download the OAuth JSON file from Google Cloud.
*   **Fix**: See [Google Cloud Setup](#3-google-cloud-setup-one-time). Ensure file is named exactly `credentials.json`.

#### "Redirected to login page" / Cookies Expired
*   **Cause**: The session cookies in the `cookie` file are old.
*   **Fix**: Run `python scripts/wigor_login.py` to regenerate them.

#### GitHub Action Fails
*   **Cause**: Secrets might be missing or incorrect.
*   **Fix**: Check Settings -> Secrets. You need `WIGOR_USERNAME`, `WIGOR_PASSWORD`, and `GOOGLE_CREDENTIALS`.

#### "Review blocked by Google" during Auth
*   **Cause**: The app is unverified (normal for personal projects).
*   **Fix**: Click "Advanced" -> "Go to Schedule Scraper (unsafe)" -> "Allow".

---

**Need to set up Automation?** Check out [QUICKSTART.md](QUICKSTART.md) for the GitHub Actions guide.
