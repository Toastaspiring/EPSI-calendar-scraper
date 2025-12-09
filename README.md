# Schedule Scraper - Automatic Calendar Sync

Automatically scrapes your schedule from WigorServices and syncs it to Google Calendar.

## 🚀 Quick Links

| Goal | Link |
| :--- | :--- |
| **I want to set up Automation** (GitHub Actions) | [**--> Go to Quick Start**](docs/QUICKSTART.md) |
| **I want to run it locally** | [**--> Go to Documentation**](docs/documentation.md) |
| **I need technical details / API docs** | [**--> Go to Documentation**](docs/documentation.md#%EF%B8%8F-technical-guide) |

---

## ✨ Features

- ✅ **Web Scraping**: Extracts schedule from WigorServices
- ✅ **Auto-Login**: Automatically handles authentication (no manual cookies needed!).
- ✅ **Google Calendar Sync**: Creates real calendar events with room, professor, and Teams links.
- ✅ **Automation**: Ready-to-go GitHub Actions workflow for weekly sync.

## 📁 Project Structure

```
PythonProject2/
├── main.py                      # Main scraper script
├── scripts/
│   ├── wigor_login.py           # Auto-login script
│   └── google_calendar_sync.py  # Calendar sync logic
├── .github/workflows/           # Automation
└── docs/                        # Documentation
```

## 🆘 Troubleshooting

If you are having issues (e.g., credentials not found, login failing), please consult the **[Detailed Troubleshooting Guide](docs/documentation.md#-troubleshooting)**.

