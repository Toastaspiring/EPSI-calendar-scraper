# WigorServices Schedule Scraper

<div align="center">

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![GitHub Actions](https://img.shields.io/badge/github%20actions-automated-green.svg)
![Outlook](https://img.shields.io/badge/Outlook-Supported-blue.svg)
![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)

**A robust, automated solution to sync your EPSI/WIS schedule directly to Google or Outlook Calendar.**

[Getting Started](docs/QUICKSTART.md) • [Documentation](docs/documentation.md) • [Troubleshooting](docs/documentation.md#-troubleshooting)

</div>

---

## Overview

This project automates the tedious task of checking your school schedule. It logs into the **WigorServices** portal, extracts your course timetable, and seamlessly synchronizes it with your **Google Calendar**.

Designed to be **"Set and Forget"**, it runs automatically via GitHub Actions every Monday morning, ensuring your calendar is always up-to-date with room numbers, professor names, and Microsoft Teams meeting links.

## Key Features

*   **Automated Authentication**: Handles login via Selenium with headless browser support.
*   **Intelligent Sync**: Parses complex HTML schedules and maps them to Google/Outlook events.
*   **Rich Event Details**: Includes Class Name, Professor, Room Location, and clickable Teams links.
*   **CI/CD Ready**: Pre-configured GitHub Actions workflow for zero-touch weekly automation.
*   **Robust Error Handling**: Auto-detects expired sessions and handles connection retries.

## Quick Start

The fastest way to use this tool is via **GitHub Actions** (Cloud automation).

1.  **Fork/Clone** this repository.
2.  **Configure Secrets** (Wigor Credentials & Calendar API).
3.  **Enable the Workflow**.

**[Read the 5-Minute Setup Guide](docs/QUICKSTART.md)**

---

## Usage Choices

### Option A: Cloud Automation (Recommended)
Run the scraper automatically on GitHub servers. No local machine required after initial setup.  
**[View Automation Guide ->](docs/QUICKSTART.md)**

### Option B: Local Execution
Run the script manually on your own machine. Ideal for development or one-off syncs.  
```bash
# Generate cookies
python scripts/wigor_login.py

# Run scraper
python main.py
```
**[View Technical Documentation ->](docs/documentation.md)**

---

## Repository Structure

```
.
├── .github/workflows/   # Automation workflows (Weekly Sync)
├── docs/                # Comprehensive guides & reference
├── scripts/             # Core utilities (Login, Google API)
├── data/                # Data artifacts (Cookies, Cache, JSON)
└── main.py              # Application entry point
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open-source and available under the [MIT License](LICENSE).
