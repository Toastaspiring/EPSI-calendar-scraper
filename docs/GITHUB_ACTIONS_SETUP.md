# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions to automatically run your schedule scraper every Monday.

## 📋 Overview

The GitHub Actions workflow will:
- ✅ Run every Monday at 6:00 AM UTC (7:00 AM CET / 8:00 AM CEST)
- ✅ Scrape your schedule from WigorServices
- ✅ Sync events to Google Calendar
- ✅ Save logs and event data as artifacts
- ✅ Can be manually triggered anytime

---

## 🚀 Setup Steps

### 1. Push Code to GitHub

First, create a GitHub repository and push your code:

```bash
# Initialize git (if not already done)
cd C:\Users\louis\PycharmProjects\PythonProject2
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Schedule scraper with automation"

# Add remote (replace with your GitHub repo)
git remote add origin https://github.com/YOUR_USERNAME/schedule-scraper.git

# Push
git push -u origin main
```

---

### 2. Set Up GitHub Secrets

GitHub Actions needs your credentials. Add them as **Repository Secrets**:

#### 2.1 Go to Repository Settings
1. Go to your GitHub repository
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

#### 2.2 Add WIGOR_COOKIE Secret

**Name:** `WIGOR_COOKIE`

**Value:** Copy the entire content of your `cookie` file:
```
ASP.NET_SessionId=cyufruoy1njpgqidkn5hcjej; .DotNetCasClientAuth=F68FFB9AD5057660CF390881F7A752CF334DF7FF395D20360F9AA4FC151E624CE4B2F25B5B3FD05E67E335DAD97AA65F76856ED93472331E61D69571209FDBE1853337FE8BA22F1389BDC4DB98F6DEC52E7AA4490478547E8330094495A580C304AC8C7DE185C8B4C9F31487142BC785CE49E0994D0F3217286BDE740CB20DFF2A52AC5D630A78FB9DA835A39517DC1EF26B1F7D8F09B3B7ED4D702129899C4FBBA1D5D758EC5DA7952279D2848C03C1820AEB067F8BBF452C09105C78E9A2DB
```

Click **Add secret**

#### 2.3 Add GOOGLE_CREDENTIALS Secret

**Name:** `GOOGLE_CREDENTIALS`

**Value:** Copy the entire content of your `credentials.json` file:
```json
{
  "installed": {
    "client_id": "887162951191-h370q9rikeom05a3heqs25n4u7ggb24i.apps.googleusercontent.com",
    "project_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    ...
  }
}
```

Click **Add secret**

---

### 3. Initial Google Authentication

GitHub Actions needs the `token.pickle` file to avoid browser authentication. Let's create it:

#### Option A: Run Locally First (Recommended)

1. Run the script locally once:
   ```bash
   python main.py
   ```

2. This creates `token.pickle` file

3. The workflow will cache this file automatically

#### Option B: Manual Trigger

1. Push the workflow to GitHub
2. Go to **Actions** tab
3. Click **Weekly Schedule Sync**
4. Click **Run workflow** → **Run workflow**
5. First run will authenticate (may need to set up service account - see below)

---

### 4. Verify Workflow

#### Check Workflow File
1. Go to your repository on GitHub
2. Navigate to `.github/workflows/schedule-sync.yml`
3. Verify the file is there

#### Test Manual Run
1. Go to **Actions** tab
2. Click **Weekly Schedule Sync** workflow
3. Click **Run workflow** button
4. Select branch (usually `main`)
5. Click **Run workflow**
6. Wait for it to complete (should take ~30 seconds)

#### Check Results
- ✅ Green checkmark = Success
- ❌ Red X = Failed (check logs)
- Click on the run to see detailed logs
- Download artifacts (logs, events.json) from the run

---

## 📅 Schedule Details

### Cron Schedule
```yaml
cron: '0 6 * * 1'
```

This means:
- `0` - Minute: 0 (top of the hour)
- `6` - Hour: 6 AM UTC
- `*` - Day of month: Any
- `*` - Month: Any
- `1` - Day of week: Monday (0=Sunday, 1=Monday, ..., 6=Saturday)

### Time Zones
- **UTC:** 6:00 AM
- **CET (Winter):** 7:00 AM
- **CEST (Summer):** 8:00 AM
- **EST:** 1:00 AM
- **PST:** 10:00 PM (Sunday night)

### Adjust Schedule
To change the schedule, edit `.github/workflows/schedule-sync.yml`:

```yaml
# Every Monday at 8 AM UTC
- cron: '0 8 * * 1'

# Every day at 6 AM UTC
- cron: '0 6 * * *'

# Every weekday at 7 AM UTC
- cron: '0 7 * * 1-5'

# Twice per week: Monday and Thursday at 6 AM UTC
- cron: '0 6 * * 1,4'
```

Use [crontab.guru](https://crontab.guru/) to help build cron expressions.

---

## 🔍 Monitoring

### View Workflow Runs
1. Go to **Actions** tab
2. See list of all runs
3. Green = Success, Red = Failed, Yellow = In Progress

### Check Logs
1. Click on a workflow run
2. Click on the job name (e.g., "scrape-and-sync")
3. Expand steps to see detailed logs
4. Look for errors in red

### Download Artifacts
Each run saves:
- **schedule-scraper-log-XXX**: Complete log file
- **events-json-XXX**: Extracted events

To download:
1. Go to workflow run
2. Scroll to bottom
3. Click artifact name to download

### Email Notifications
GitHub will email you if a workflow fails (by default).

Configure in: Settings → Notifications → Actions

---

## 🔒 Security Best Practices

### ✅ DO:
- Use GitHub Secrets for sensitive data
- Keep credentials.json private
- Regularly update cookies when they expire
- Use `.gitignore` to prevent committing secrets

### ❌ DON'T:
- Commit `cookie` file to repository
- Commit `credentials.json` to repository
- Commit `token.pickle` to repository
- Share your GitHub secrets

### Files Protected by .gitignore:
```
cookie
credentials.json
token.pickle
*.log
```

---

## 🛠️ Troubleshooting

### Workflow Not Running

**Check:**
1. Go to **Actions** tab
2. Check if workflow is listed
3. Verify `.github/workflows/schedule-sync.yml` exists
4. Check if Actions are enabled (Settings → Actions → General)

### Authentication Errors

**Cookie Expired:**
```
ERROR - Received a login page. Cookies have expired!
```

**Fix:**
1. Get fresh cookie from browser
2. Update `WIGOR_COOKIE` secret in GitHub
3. Re-run workflow

**Google Authentication Failed:**
```
ERROR - credentials.json not found!
```

**Fix:**
1. Verify `GOOGLE_CREDENTIALS` secret exists
2. Check JSON format is correct
3. Ensure no extra spaces or newlines

### No Events Created

**Check logs for:**
- Cookie expiration
- Network errors
- Google Calendar API quota

**Fix:**
- Update cookies
- Check Google Cloud Console quota
- Verify credentials are valid

### Token Cache Issues

**Problem:** Workflow keeps asking for authentication

**Fix:**
1. Run locally once to create `token.pickle`
2. The workflow caches it automatically
3. Or set up a service account (advanced)

---

## 🔄 Updating Cookies

When cookies expire:

### Method 1: GitHub Web Interface
1. Go to repository → Settings → Secrets and variables → Actions
2. Click on `WIGOR_COOKIE`
3. Click **Update secret**
4. Paste new cookie value
5. Click **Update secret**

### Method 2: GitHub CLI
```bash
# Install GitHub CLI: https://cli.github.com/
gh secret set WIGOR_COOKIE < cookie
```

### Method 3: Automation Script
Create `update_secrets.sh`:
```bash
#!/bin/bash
gh secret set WIGOR_COOKIE < cookie
echo "Cookie updated!"
```

---

## 📊 Workflow Features

### Automatic Features
- ✅ Runs every Monday at 6 AM UTC
- ✅ Installs Python dependencies
- ✅ Uses cached Python packages (faster)
- ✅ Saves logs as artifacts
- ✅ Saves events.json as artifacts
- ✅ Caches Google authentication token
- ✅ Notifies on failure

### Manual Trigger
You can run the workflow anytime:
1. Go to **Actions** tab
2. Click **Weekly Schedule Sync**
3. Click **Run workflow**
4. Select branch
5. Click **Run workflow** button

### Artifacts
Artifacts are saved for:
- **Logs:** 30 days
- **Events JSON:** 7 days

You can download them from completed workflow runs.

---

## 🚀 Advanced Configuration

### Run More Frequently

Edit `.github/workflows/schedule-sync.yml`:

```yaml
on:
  schedule:
    # Monday and Thursday at 6 AM
    - cron: '0 6 * * 1,4'
    # Or daily
    - cron: '0 6 * * *'
```

### Add Notifications

Use GitHub Actions marketplace:
- [Slack notifications](https://github.com/marketplace/actions/slack-send)
- [Discord notifications](https://github.com/marketplace/actions/discord-message-notify)
- [Email notifications](https://github.com/marketplace/actions/send-email)

Example (Slack):
```yaml
- name: Notify Slack on Success
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    payload: |
      {
        "text": "✅ Schedule synced successfully!"
      }
  env:
    SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

### Service Account (No Browser Auth)

For fully automated Google Calendar access:

1. Create service account in Google Cloud Console
2. Download service account key JSON
3. Share calendar with service account email
4. Add service account key as secret
5. Update `google_calendar_sync.py` to use service account

See: https://developers.google.com/identity/protocols/oauth2/service-account

---

## 📋 Checklist

Before pushing to GitHub:

- [ ] `.gitignore` includes sensitive files
- [ ] Code works locally with `python main.py`
- [ ] `requirements.txt` is up to date
- [ ] Created GitHub repository
- [ ] Pushed code to GitHub
- [ ] Added `WIGOR_COOKIE` secret
- [ ] Added `GOOGLE_CREDENTIALS` secret
- [ ] Tested manual workflow run
- [ ] Checked workflow logs
- [ ] Verified events in Google Calendar
- [ ] Set up failure notifications (optional)

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Cron Schedule Examples](https://crontab.guru/)
- [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

## 💡 Tips

### Save Costs
GitHub Actions is free for public repositories and includes 2,000 minutes/month for private repos. This workflow uses ~1 minute per run, so 4-8 runs per month is well within limits.

### Monitor Usage
- Settings → Billing → Actions usage
- Track minutes used per month

### Optimize Performance
- Use caching (already implemented)
- Minimize dependencies
- Run only when needed

---

## ✨ Summary

Your schedule scraper will now:

1. **Run automatically** every Monday at 6 AM UTC
2. **Scrape schedule** from WigorServices
3. **Extract events** with dates across the week
4. **Sync to Google Calendar** automatically
5. **Save logs** for monitoring
6. **Notify on failure** via email

**All happening in the cloud with zero local setup needed!** 🎉

---

## 🆘 Need Help?

1. Check workflow logs in Actions tab
2. Review this guide's troubleshooting section
3. Check GitHub Actions documentation
4. Verify secrets are set correctly
5. Test locally first with `python main.py`

---

**Ready to deploy? Push to GitHub and watch it run!** 🚀

