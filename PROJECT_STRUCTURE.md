# Project Structure

```
PythonProject2/
│
├── 📄 Core Files
│   ├── main.py                          # Main scraper script
│   ├── google_calendar_sync.py          # Google Calendar integration
│   ├── requirements.txt                 # Python dependencies
│   ├── README.md                        # Project overview
│   └── .gitignore                       # Git ignore rules
│
├── 🔧 Configuration & Secrets (gitignored)
│   ├── cookie                           # WigorServices auth cookies
│   ├── credentials.json                 # Google OAuth credentials
│   └── token.pickle                     # Google auth token cache
│
├── 📁 .github/
│   └── workflows/
│       └── schedule-sync.yml            # GitHub Actions automation
│
├── 📚 docs/                             # All Documentation
│   ├── README.md                        # Main documentation
│   ├── QUICKSTART.md                    # ⭐ 5-minute setup
│   │
│   ├── Google Calendar Setup
│   ├── GOOGLE_CALENDAR_SETUP.md         # Detailed Google setup
│   ├── SETUP_CHECKLIST.md               # Setup checklist
│   │
│   ├── Automation Guides
│   ├── GITHUB_ACTIONS_QUICKREF.md       # ⭐ GitHub Actions quick ref
│   ├── GITHUB_ACTIONS_SETUP.md          # Detailed GitHub Actions
│   ├── GITHUB_ACTIONS_COMPLETE.md       # Complete GitHub guide
│   ├── CRON_SETUP.md                    # Local cron/Task Scheduler
│   ├── AUTOMATION_SUMMARY.md            # Automation overview
│   │
│   └── Additional Documentation
│       └── COMPLETION_SUMMARY.md        # Project completion summary
│
├── 🧪 tests/                            # Test Scripts
│   ├── test_setup.py                    # Test system setup
│   ├── test_dates.py                    # Test date extraction
│   ├── test_automation.py               # Test automation readiness
│   └── test_cron.py                     # Test cron execution
│
├── 🔧 scripts/                          # Helper Scripts
│   └── cron_run.py                      # Cron wrapper script
│
├── 📊 data/                             # Data Files (gitignored)
│   ├── events.json                      # Extracted events
│   └── raw                              # Raw HTML from scraping
│
├── 📝 logs/                             # Log Files (gitignored)
│   └── schedule_scraper.log             # Application logs
│
└── 🐍 Python Environment
    ├── .venv/                           # Virtual environment (gitignored)
    ├── __pycache__/                     # Python cache (gitignored)
    └── .idea/                           # IDE config (gitignored)
```

## 📂 Folder Organization

### Root Level
**Core application files only**
- Main scripts (`main.py`, `google_calendar_sync.py`)
- Configuration (`requirements.txt`, `.gitignore`)
- Root README (project overview)

### `docs/` - Documentation
**All documentation in one place**
- Setup guides
- User manuals
- Configuration instructions
- Troubleshooting guides

### `tests/` - Tests
**All test scripts**
- Setup verification
- Feature testing
- Integration testing

### `scripts/` - Helper Scripts
**Utility and wrapper scripts**
- Cron wrappers
- Maintenance scripts
- Setup helpers

### `data/` - Data Files
**Generated/downloaded data** (gitignored)
- Extracted events JSON
- Raw HTML files
- Cache files

### `logs/` - Log Files
**Application logs** (gitignored)
- Execution logs
- Error logs
- Debug information

### `.github/` - GitHub Configuration
**GitHub-specific files**
- Actions workflows
- Issue templates (future)
- PR templates (future)

## 🔒 Security

### Gitignored Files/Folders
These are never committed to the repository:
- `cookie` - Authentication cookies
- `credentials.json` - Google OAuth secrets
- `token.pickle` - Google auth token
- `data/` - All data files
- `logs/` - All log files
- `.venv/` - Virtual environment
- `__pycache__/` - Python bytecode
- `.idea/` - IDE configuration

### Committed Files
Only these are in version control:
- Source code (`*.py`)
- Documentation (`docs/*.md`)
- Configuration (`requirements.txt`, `.gitignore`)
- GitHub workflows (`.github/workflows/*.yml`)
- Root README

## 📋 File Purposes

### Core Scripts
- **`main.py`**: Entry point, scraping logic, event extraction
- **`google_calendar_sync.py`**: Google Calendar API integration

### Documentation
- **`docs/QUICKSTART.md`**: Start here! 5-minute setup
- **`docs/README.md`**: Complete feature documentation
- **`docs/GOOGLE_CALENDAR_SETUP.md`**: Detailed Google Calendar setup
- **`docs/GITHUB_ACTIONS_QUICKREF.md`**: Quick GitHub Actions reference
- **`docs/GITHUB_ACTIONS_SETUP.md`**: Complete GitHub Actions guide
- **`docs/CRON_SETUP.md`**: Local automation setup

### Tests
- **`tests/test_setup.py`**: Verify system requirements
- **`tests/test_dates.py`**: Test date extraction
- **`tests/test_automation.py`**: Comprehensive automation test
- **`tests/test_cron.py`**: Test cron compatibility

### Configuration
- **`requirements.txt`**: Python package dependencies
- **`.gitignore`**: Git ignore rules
- **`.github/workflows/schedule-sync.yml`**: GitHub Actions workflow

## 🎯 Benefits of This Structure

### ✅ Clean Root Directory
- Only essential files in root
- Easy to navigate
- Professional appearance

### ✅ Organized Documentation
- All docs in one place
- Easy to find information
- Logical grouping

### ✅ Separated Concerns
- Tests separate from main code
- Scripts in their own folder
- Data and logs isolated

### ✅ Git-Friendly
- Sensitive files properly gitignored
- Clean git history
- Easy collaboration

### ✅ Scalable
- Easy to add new features
- Simple to add more tests
- Room for growth

## 🚀 Navigation

### Want to get started?
👉 Read `docs/QUICKSTART.md`

### Need to set up Google Calendar?
👉 Read `docs/GOOGLE_CALENDAR_SETUP.md`

### Want to automate with GitHub Actions?
👉 Read `docs/GITHUB_ACTIONS_QUICKREF.md`

### Need to debug an issue?
👉 Check `logs/schedule_scraper.log`

### Want to see extracted data?
👉 Look at `data/events.json`

### Need to run tests?
👉 Run `python tests/test_setup.py`

---

**Clean, organized, and professional!** ✨

