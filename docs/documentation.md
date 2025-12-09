# WigorServices Schedule Scraper - Documentation

**Complete guide to setting up, running, and integrating with the WigorServices Schedule Scraper.**

---

## Table of Contents
1. [Project Overview](#-project-overview)
2. [Setup Guide (Local & Google Cloud)](#-setup-guide)
3. [Technical Guide (API & Integration)](#-technical-guide)
4. [Outlook Integration](#-outlook-integration)
5. [Troubleshooting](#-troubleshooting)

---

## Project Overview

This tool scrapes your schedule from the WigorServices EDT (timetable) system and extracts all calendar events. It can run locally or automatically in the cloud via GitHub Actions.

### Features
- **Fetch schedule page**: Authenticates via cookies or auto-login.
- **Extract events**: KPI-driven parsing of HTML schedule.
- **Export to JSON**: Structured data for easy processing.
- **Google/Outlook Sync**: Automatically pushes events to your Google or Outlook Calendar.
- **Teams Links**: Preserves Microsoft Teams meeting links.

### Project Structure
```
PythonProject2/
├── main.py                      # Main scraper script
├── scripts/
│   ├── wigor_login.py           # Auto-login & Cookie generation
│   ├── google_calendar_sync.py  # Google Sync script
│   └── outlook_calendar_sync.py # Outlook Sync script
├── .github/workflows/           # Automation
├── data/                        # JSON & Raw HTML output
├── logs/                        # Execution logs
└── docs/                        # You are here
```

---

## Setup Guide

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

## Technical Guide

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

### Options
*   `--no-sync`: Skip calendar sync entirely.
*   `--provider`: Choose `GOOGLE`, `OUTLOOK`, or `BOTH`.

---

## 4. Outlook Setup (One-Time)

To sync your schedule with Microsoft Outlook, you need to register an "App" in **Microsoft Azure** to get a Client ID and Secret.

### 4.1 Register App in Azure Portal

1.  Go to the [Azure Portal - App Registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade).
2.  Log in with your Microsoft account (the same one you use for Outlook).
3.  Click **New Registration**.
4.  **Name**: `Schedule Scraper` (or any name you like).
5.  **Supported Account Types**: Select **"Accounts in any organizational directory (Any Azure AD directory - Multitenant) and personal Microsoft accounts (e.g. Skype, Xbox)"**.
    *   *Note: This is critical for personal Outlook accounts.*
6.  **Redirect URI**:
    *   Platform: **Web**
    *   URI: `https://login.microsoftonline.com/common/oauth2/nativeclient`
7.  Click **Register**.

### 4.2 Get Client ID & Secret

Once created, you will be on the Overview page.

1.  **Client ID**: Copy the **Application (client) ID**. This is your `MS_CLIENT_ID`.
2.  **Client Secret**:
    *   Click **Certificates & secrets** (left sidebar).
    *   Click **New client secret**.
    *   Description: `Scraper Secret`
    *   Expires: `24 months` (or custom).
    *   Click **Add**.
    *   **COPY THE VALUE NOW**. You won't see it again. This is your `MS_CLIENT_SECRET`.

### 4.3 Configure Permissions (Scopes)

1.  Click **API Permissions** (left sidebar).
2.  Click **Add a permission**.
3.  Select **Microsoft Graph**.
4.  Select **Delegated permissions**.
5.  Search for and check: `Calendars.ReadWrite`.
6.  Click **Add permissions**.

### 4.4 Run Locally to Generate Token

Similar to Google, you need to authenticate once locally to generate a token for the headless GitHub Action.

1.  Set your credentials in your terminal:
    ```powershell
    $env:MS_CLIENT_ID="your_client_id_here"
    $env:MS_CLIENT_SECRET="your_client_secret_here"
    ```
2.  Run the sync script (it handles auth if not found):
    ```bash
    python main.py --sync-only --provider OUTLOOK
    ```
3.  Follow the link in the terminal, login, and copy the return URL back to the terminal.
4.  **Success!** A file `data/o365_token.txt` will be created.

### 4.5 Get the Base64 Token for GitHub
Run this in PowerShell after generating the token file:
```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes('data/o365_token.txt'))
```
Use this value for the `MS_TOKEN_BASE64` secret.

---

## Troubleshooting

### Common Issues

#### `credentials.json` not found
*   **Cause**: You didn't download the OAuth JSON file from Google Cloud.
*   **Fix**: See [Google Cloud Setup](#3-google-cloud-setup-one-time). Ensure file is named exactly `credentials.json`.

#### "Redirected to login page" / Cookies Expired
*   **Cause**: The session cookies in the `cookie` file are old.
*   **Fix**: Run `python scripts/wigor_login.py` to regenerate them.

#### GitHub Action Fails
*   **Cause**: Secrets might be missing or incorrect.
*   **Fix**: Check Settings -> Secrets. You need `WIGOR_USERNAME`, `WIGOR_PASSWORD`, `GOOGLE_CREDENTIALS`, and **`GOOGLE_TOKEN_BASE64`**.
    *   *See [QUICKSTART.md](QUICKSTART.md) for how to generate the base64 token.*

#### "Review blocked by Google" during Auth
*   **Cause**: The app is unverified (normal for personal projects).
*   **Fix**: Click "Advanced" -> "Go to Schedule Scraper (unsafe)" -> "Allow".

---

**Need to set up Automation?** Check out [QUICKSTART.md](QUICKSTART.md) for the GitHub Actions guide.
