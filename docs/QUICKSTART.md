# Quick Start: Automated Schedule Sync

**The "Happy Path" to getting your schedule properly synced automatically every week using GitHub Actions.**

This guide assumes you want a **Set It and Forget It** solution. We will use GitHub Actions to run the scraper every Monday morning.

---

## Prerequisites
1.  **GitHub Account**
2.  **WigorServices Credentials** (Username & Password)
3.  **Google Cloud Credentials** (for Calendar Sync)
    *   *If you haven't created these yet, see the [Setup Guide in documentation.md](documentation.md#3-google-cloud-setup-one-time).*

---

## Setup Steps (5 Minutes)

### 1. Push to GitHub
If you haven't already, push this code to a new private GitHub repository.
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

### 2. Configure Secrets
Go to your repository on GitHub:
1.  Click **Settings** (top bar).
2.  Click **Secrets and variables** -> **Actions** (left sidebar).
3.  Click **New repository secret**.

Add the following 4 secrets:

### Secrets Configuration
You need to set up secrets depending on your provider (Google or Outlook).

**Common Secrets (Required for both):**
| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `WIGOR_USERNAME` | Your Wigor username | E.g. `louis.marec` |
| `WIGOR_PASSWORD` | Your Wigor password | |
| `CALENDAR_PROVIDER` | `GOOGLE`, `OUTLOOK`, or `BOTH` | Default is `GOOGLE` |

#### Option A: Google Calendar Secrets
| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `GOOGLE_CREDENTIALS` | Content of `credentials.json` | *See docs for setup* |
| `GOOGLE_TOKEN_BASE64` | Base64 encoded `token.pickle` | **See below** |

#### Option B: Outlook Calendar Secrets
| Secret Name | Value | Description |
| :--- | :--- | :--- |
| `MS_CLIENT_ID` | Application (Client) ID | From Azure Portal |
| `MS_CLIENT_SECRET` | Client Secret Value | From Azure Portal |
| `MS_TOKEN_BASE64` | Base64 encoded `o365_token.txt` | **See below** |

#### How to get the `*_TOKEN_BASE64` secret
Since GitHub servers can't open a browser, you must authenticate locally first.

1.  Run the script locally to generate the token file (`data/token.pickle` for Google, `data/o365_token.txt` for Outlook).
2.  Run this PowerShell command to convert it:
    ```powershell
    # For Google
    [Convert]::ToBase64String([IO.File]::ReadAllBytes('data/token.pickle'))

    # For Outlook
    [Convert]::ToBase64String([IO.File]::ReadAllBytes('data/o365_token.txt'))
    ```
3.  Copy the huge string output and paste it as the secret value.

### 3. Trigger the Workflow
1.  Go to the **Actions** tab in your repository.
2.  Select **Weekly Schedule Sync** from the left sidebar.
3.  Click **Run workflow** (blue button).

---

## What Happens Next?
1.  **Authentication**: The action spins up a virtual browser, logs in as you, and grabs fresh cookies.
2.  **Scraping**: It fetches your schedule for the current week.
3.  **Sync**: It uploads the events to your Google Calendar.
4.  **Repeat**: This will now happen **automatically every Monday at 6:00 AM UTC**.

---

## Verification
*   **Check Calendar**: Open Google Calendar and look for your courses.
*   **Check Logs**: click on the specific run in the "Actions" tab to see detailed logs if something goes wrong.

> **Need to debug?** Check [docs/documentation.md](documentation.md) for detailed troubleshooting.
