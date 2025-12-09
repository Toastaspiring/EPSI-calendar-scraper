# 🚀 Quick Start: Automated Schedule Sync

**The "Happy Path" to getting your schedule properly synced automatically every week using GitHub Actions.**

This guide assumes you want a **Set It and Forget It** solution. We will use GitHub Actions to run the scraper every Monday morning.

---

## ✅ Prerequisites
1.  **GitHub Account**
2.  **WigorServices Credentials** (Username & Password)
3.  **Google Cloud Credentials** (for Calendar Sync)
    *   *If you haven't created these yet, see the [Setup Guide in documentation.md](documentation.md#3-google-cloud-setup-one-time).*

---

## ⚡ Setup Steps (5 Minutes)

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

Add the following 3 secrets:

| Secret Name | Value |
| :--- | :--- |
| `WIGOR_USERNAME` | Your Wigor username (e.g., `louis.marec`) |
| `WIGOR_PASSWORD` | Your Wigor password |
| `GOOGLE_CREDENTIALS` | The content of your `credentials.json` file |

### 3. Trigger the Workflow
1.  Go to the **Actions** tab in your repository.
2.  Select **Weekly Schedule Sync** from the left sidebar.
3.  Click **Run workflow** (blue button).

---

## 🎉 What Happens Next?
1.  **Authentication**: The action spins up a virtual browser, logs in as you, and grabs fresh cookies.
2.  **Scraping**: It fetches your schedule for the current week.
3.  **Sync**: It uploads the events to your Google Calendar.
4.  **Repeat**: This will now happen **automatically every Monday at 6:00 AM UTC**.

---

## 🔍 Verification
*   **Check Calendar**: Open Google Calendar and look for your courses.
*   **Check Logs**: click on the specific run in the "Actions" tab to see detailed logs if something goes wrong.

> **Need to debug?** Check [docs/documentation.md](documentation.md) for detailed troubleshooting.
