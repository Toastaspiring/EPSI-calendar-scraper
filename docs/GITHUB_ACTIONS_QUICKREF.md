# GitHub Actions - Quick Reference

## 🚀 Quick Setup (5 Minutes)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Add schedule scraper with GitHub Actions"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

### 2. Add Secrets
Go to: **Repository → Settings → Secrets and variables → Actions**

Add two secrets:

**WIGOR_COOKIE:**
```
ASP.NET_SessionId=xxx; .DotNetCasClientAuth=xxx
```

**GOOGLE_CREDENTIALS:**
```json
{
  "installed": {
    "client_id": "...",
    ...
  }
}
```

### 3. Test Run
**Actions tab → Weekly Schedule Sync → Run workflow**

### 4. Done! ✅
It will now run every Monday at 6 AM UTC automatically.

---

## 📅 Schedule

**Current:** Every Monday at 6 AM UTC (7 AM CET)

**Change schedule:** Edit `.github/workflows/schedule-sync.yml`

```yaml
# Daily at 6 AM
- cron: '0 6 * * *'

# Monday & Thursday at 6 AM  
- cron: '0 6 * * 1,4'

# Weekdays at 7 AM
- cron: '0 7 * * 1-5'
```

---

## 🔍 Monitor

### View Runs
**Actions tab** → See all workflow runs

### Check Logs
**Actions tab → Click run → Click job → Expand steps**

### Download Logs
**Scroll to bottom of run → Click artifact**

---

## 🛠️ Common Tasks

### Update Cookie (When Expired)
**Settings → Secrets and variables → Actions → WIGOR_COOKIE → Update**

### Manual Run
**Actions → Weekly Schedule Sync → Run workflow**

### View Schedule
**Actions → Weekly Schedule Sync** (shows next run time)

### Disable Auto-Run
**Actions → Weekly Schedule Sync → ⋯ → Disable workflow**

---

## ⚠️ Troubleshooting

### Cookie Expired
Update `WIGOR_COOKIE` secret with fresh value from browser

### No Events
Check logs in Actions tab for errors

### Workflow Not Running
1. Check if workflow is enabled
2. Verify `.github/workflows/schedule-sync.yml` exists
3. Check Settings → Actions → General

---

## 📊 Costs

**Free tier:** 2,000 minutes/month (private repos)

**This workflow:** ~1 minute per run

**4 runs/month:** Well within free tier ✅

---

## 🔐 Security

✅ Secrets are encrypted
✅ .gitignore protects sensitive files
✅ Never commit credentials
✅ Update cookies when expired

---

## 💡 Quick Commands

```bash
# Test locally first
python main.py

# Check workflow syntax
cat .github/workflows/schedule-sync.yml

# Push changes
git add .
git commit -m "Update workflow"
git push
```

---

## 📚 Full Guide

See `GITHUB_ACTIONS_SETUP.md` for complete documentation.

---

**That's it! Your schedule syncs automatically every Monday.** 🎉

