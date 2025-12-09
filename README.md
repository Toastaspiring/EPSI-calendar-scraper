# Schedule Scraper - Automatic Calendar Sync

Automatically scrapes your schedule from WigorServices and syncs it to Google Calendar.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate fresh cookies (no more manual copying!)
python scripts/wigor_login.py

# Run the scraper (automatically syncs to Google Calendar)
python main.py

# Or scrape without syncing
python main.py --no-sync
```

### 🔄 Automatic Cookie Generation

**No more manual cookie copying from browser DevTools!**

The `wigor_login.py` script automates the entire login process:
- Opens browser automatically
- Logs in with your credentials
- Captures cookies
- Saves to `cookie` file
- Verifies they work

**See:** [docs/AUTO_LOGIN_GUIDE.md](docs/AUTO_LOGIN_GUIDE.md)

## 📁 Project Structure

```
PythonProject2/
├── main.py                      # Main scraper script
├── google_calendar_sync.py      # Google Calendar integration
├── requirements.txt             # Python dependencies
├── .gitignore                   # Git ignore rules
│
├── .github/
│   └── workflows/
│       └── schedule-sync.yml    # GitHub Actions automation
│
├── docs/                        # 📚 All documentation
│   ├── README.md               # Main documentation
│   ├── QUICKSTART.md           # Quick setup guide
│   ├── GOOGLE_CALENDAR_SETUP.md
│   ├── GITHUB_ACTIONS_SETUP.md
│   ├── CRON_SETUP.md
│   └── ...
│
├── tests/                       # 🧪 Test scripts
│   ├── test_setup.py
│   ├── test_dates.py
│   ├── test_automation.py
│   └── test_cron.py
│
├── scripts/                     # 🔧 Helper scripts
│   └── cron_run.py
│
├── data/                        # 📊 Data files (gitignored)
│   ├── events.json
│   └── raw
│
├── logs/                        # 📝 Log files (gitignored)
│   └── schedule_scraper.log
│
└── [credentials]                # 🔒 Auth files (gitignored)
    ├── cookie
    ├── credentials.json
    └── token.pickle
```

## ✨ Features

- ✅ **Web Scraping**: Extracts schedule from WigorServices
- ✅ **Date Extraction**: Automatically extracts dates for each event (Monday-Friday)
- ✅ **Google Calendar Sync**: Creates events with full details
- ✅ **Automation**: Run via cron, Task Scheduler, or GitHub Actions
- ✅ **Logging**: Comprehensive logging for monitoring
- ✅ **No Prompts**: Fully automated, no user interaction needed

## 📚 Documentation

All documentation is in the `docs/` folder:

| File | Description |
|------|-------------|
| **Quick Start** ||
| [QUICKSTART.md](docs/QUICKSTART.md) | ⭐ 5-minute setup guide |
| [README.md](docs/README.md) | Complete documentation |
||
| **Google Calendar** ||
| [GOOGLE_CALENDAR_SETUP.md](docs/GOOGLE_CALENDAR_SETUP.md) | Detailed Google setup |
| [SETUP_CHECKLIST.md](docs/SETUP_CHECKLIST.md) | Interactive checklist |
||
| **Automation** ||
| [GITHUB_ACTIONS_QUICKREF.md](docs/GITHUB_ACTIONS_QUICKREF.md) | ⭐ GitHub Actions quick ref |
| [GITHUB_ACTIONS_SETUP.md](docs/GITHUB_ACTIONS_SETUP.md) | Detailed GitHub Actions guide |
| [CRON_SETUP.md](docs/CRON_SETUP.md) | Local cron/Task Scheduler setup |
| [AUTOMATION_SUMMARY.md](docs/AUTOMATION_SUMMARY.md) | Automation features overview |

## 🎯 Usage

### Basic Usage
```bash
# Full scrape + Google Calendar sync
python main.py

# Scrape only (no calendar sync)
python main.py --no-sync

# Sync only (use existing data/events.json)
python main.py --sync-only

# Show help
python main.py --help
```

### Automated Runs

**GitHub Actions (Recommended)** ⭐
- Runs automatically every Monday at 6 AM UTC
- No local computer needed
- See: [docs/GITHUB_ACTIONS_QUICKREF.md](docs/GITHUB_ACTIONS_QUICKREF.md)

**Local Cron/Task Scheduler**
- Set up weekly/daily runs on your computer
- See: [docs/CRON_SETUP.md](docs/CRON_SETUP.md)

## 🧪 Testing

```bash
# Test setup
python tests/test_setup.py

# Test automation readiness
python tests/test_automation.py

# Test date extraction
python tests/test_dates.py
```

## 📊 Monitoring

### View Logs
```bash
# Last 20 lines
tail -20 logs/schedule_scraper.log   # Linux/Mac
Get-Content logs/schedule_scraper.log -Tail 20   # Windows

# Watch in real-time
tail -f logs/schedule_scraper.log   # Linux/Mac
Get-Content logs/schedule_scraper.log -Wait   # Windows
```

### Check Data
```bash
# View extracted events
cat data/events.json   # Linux/Mac
Get-Content data/events.json   # Windows
```

## 🔒 Security

**Protected files (not in git):**
- `cookie` - Authentication cookies
- `credentials.json` - Google OAuth credentials
- `token.pickle` - Google auth token
- `data/` - Scraped data
- `logs/` - Log files

**Update cookies when expired:**
1. Get fresh cookies from browser DevTools
2. Update `cookie` file
3. Re-run script

## 🔧 Requirements

- Python 3.7+
- Internet connection
- Valid WigorServices cookies
- Google Calendar API credentials (for sync)

See `requirements.txt` for Python packages.

## 📖 Getting Started

1. **Read quick start:** [docs/QUICKSTART.md](docs/QUICKSTART.md)
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Set up Google Calendar:** [docs/GOOGLE_CALENDAR_SETUP.md](docs/GOOGLE_CALENDAR_SETUP.md)
4. **Run:** `python main.py`
5. **Set up automation:** [docs/GITHUB_ACTIONS_QUICKREF.md](docs/GITHUB_ACTIONS_QUICKREF.md)

## 🆘 Troubleshooting

**Cookie expired:**
- Update `cookie` file with fresh value from browser

**No events extracted:**
- Check logs in `logs/schedule_scraper.log`
- Verify cookie is valid

**Google Calendar errors:**
- Verify `credentials.json` exists
- Check token.pickle is valid
- See [docs/GOOGLE_CALENDAR_SETUP.md](docs/GOOGLE_CALENDAR_SETUP.md)

## 🎊 What You Get

Each run:
1. Scrapes your weekly schedule (Monday-Friday)
2. Extracts ~13 events with dates
3. Creates Google Calendar events with:
   - Course name
   - Professor
   - Room location
   - Exact times
   - Teams meeting links
   - Reminders (30 min & 10 min before)
4. Saves logs for monitoring
5. Exits with proper status code

---

**⭐ Start here:** [docs/QUICKSTART.md](docs/QUICKSTART.md)

**Need help?** Check the documentation in `docs/` folder!

