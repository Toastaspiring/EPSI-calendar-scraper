# WigorServices API Documentation

Complete technical documentation for integrating with WigorServices schedule system.

---

## Table of Contents

1. [Authentication Flow](#authentication-flow)
2. [Schedule API Endpoint](#schedule-api-endpoint)
3. [Event Data Structure](#event-data-structure)
4. [Code Examples](#code-examples)
5. [Integration Guide](#integration-guide)

---

## Authentication Flow

### Overview

WigorServices uses a **CAS (Central Authentication Service)** based authentication system with cookie-based sessions.

### Step-by-Step Authentication

#### 1. Initial Request (Triggers Redirect)

**Request:**
```http
GET /WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date=11/18/2025
Host: ws-edt-cd.wigorservices.net
```

**Note:** Replace `{username}` with the actual user's login username (e.g., "louis.marec", "john.doe")

**Response:**
- HTTP 302 Redirect to CAS login page
- Location: `https://cas-p.wigorservices.net/cas/login?service=...`

#### 2. CAS Login Page

**URL:**
```
https://cas-p.wigorservices.net/cas/login?service=https%3A%2F%2Fws-edt-cd.wigorservices.net%2FWebPsDyn.aspx%3FAction%3DposEDTLMS%26...
```

**Form Structure:**
```html
<form id="fm1" method="post" action="/cas/login">
    <input type="text" id="username" name="username" />
    <input type="password" id="password" name="password" />
    <button type="submit" id="submitBtn">SE CONNECTER</button>
</form>
```

**Form Fields:**
- `username`: Your WigorServices username (e.g., "louis.marec", "john.doe")
- `password`: Your password
- `execution`: Hidden field (auto-populated by server)
- `_eventId`: "submit" (auto-populated)

**Important:** The username entered here must match the `Tel` parameter in subsequent API requests.

#### 3. Login Submission

**Request:**
```http
POST /cas/login?service=...
Host: cas-p.wigorservices.net
Content-Type: application/x-www-form-urlencoded

username={your_username}&password={your_password}&execution=e1s1&_eventId=submit
```

**Response:**
- HTTP 302 Redirect back to service
- Sets cookies: 
  - `TGC` (Ticket Granting Cookie) - CAS session
  - May set additional session cookies

#### 4. Service Ticket Validation

**Request:**
```http
GET /WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&ticket=ST-123456-abc...
Host: ws-edt-cd.wigorservices.net
```

**Response:**
- HTTP 200 OK (if ticket valid)
- Sets application cookies:
  - `ASP.NET_SessionId`: ASP.NET session identifier
  - `.DotNetCasClientAuth`: CAS authentication token
- Returns schedule HTML page

#### 5. Subsequent Requests

**Request:**
```http
GET /WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date=11/18/2025
Host: ws-edt-cd.wigorservices.net
Cookie: ASP.NET_SessionId=abc123; .DotNetCasClientAuth=xyz789...
```

**Response:**
- HTTP 200 OK
- Returns schedule HTML directly (no redirect)

### Required Cookies

After successful authentication, you need these cookies for API requests:

```
ASP.NET_SessionId=<session_id>
.DotNetCasClientAuth=<auth_token>
```

**Cookie Format:**
```
ASP.NET_SessionId=ucrfl2phgniyfkgg5uw4gybc; .DotNetCasClientAuth=E47CF06CC20CA545AD977A8039298AB1475...
```

**Cookie Lifetime:**
- Session-based (expires when browser closes)
- Typically valid for 1-2 hours after last activity
- Must be refreshed periodically

---

## Schedule API Endpoint

### Base URL

```
https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx
```

### Query Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `Action` | Yes | API action type | `posEDTLMS` |
| `serverID` | Yes | Server identifier | `C` |
| `Tel` | Yes | User identifier/username (must match logged-in user) | `louis.marec`, `john.doe` |
| `date` | Yes | Reference date (MM/DD/YYYY) | `11/18/2025` |

### Complete Request Example

**URL:**
```
https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date=11/18/2025
```

**Example:**
```
https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=louis.marec&date=11/18/2025
```

**Headers:**
```http
GET /WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date=11/18/2025 HTTP/1.1
Host: ws-edt-cd.wigorservices.net
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Cookie: ASP.NET_SessionId=abc123; .DotNetCasClientAuth=xyz789...
Connection: keep-alive
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Encoding: gzip

<!DOCTYPE html>
<html>
  <!-- Schedule HTML -->
</html>
```

### Date Parameter Behavior

The `date` parameter returns the **week containing that date**:

- If `date=11/18/2025` (Tuesday), returns Mon 11/17 - Fri 11/21
- If `date=11/17/2025` (Monday), returns Mon 11/17 - Fri 11/21
- Always returns full week (Monday to Friday)

---

## Event Data Structure

### HTML Structure

Events are represented as `<div class="Case">` elements with inline styling and nested tables.

#### Event Container

```html
<div class="Case" style="position:absolute;top:XXX%;left:XXX%;width:XXX%;height:XXX%;background-color:rgb(XXX,XXX,XXX);">
  <table class="TCase">
    <!-- Event details -->
  </table>
</div>
```

**Style Attributes:**
- `top`: Vertical position (time of day)
- `left`: Horizontal position (day of week)
- `width`: Duration width
- `height`: Duration height
- `background-color`: Event type color

#### Event Table Structure

```html
<table class="TCase">
  <tbody>
    <tr>
      <td class="TCase">
        <!-- Course name -->
        Entrepots de données (Datamart)
        
        <div class="Teams">
          <!-- Teams links -->
        </div>
      </td>
    </tr>
    <tr>
      <td class="TCProf">
        <!-- Professor name -->
        causeur yann
        <br/>
        <!-- Group name -->
        CC MASTERE 1 CYBER + INFRA + ECDPIA + EID 25/26
        
        <img title="Présenciel" src="..."/>
      </td>
    </tr>
    <tr>
      <td class="TChdeb">
        <!-- Time -->
        10:00 - 12:00
      </td>
    </tr>
    <tr>
      <td class="TCSalle">
        <!-- Room -->
        Salle:201-EPSI(ST EXUPERY)
      </td>
    </tr>
  </tbody>
</table>
```

### Day Headers

Days are marked with `<div class="Jour">` elements:

```html
<div class="Jour" style="top:105.0000%;left:103.0000%;height:5.00%;">
  <table class="TCase">
    <tr>
      <td class="TCJour">Lundi 17 Novembre</td>
    </tr>
  </table>
</div>
```

**Position Mapping:**
- `left:3.0000%` → Monday
- `left:22.4000%` → Tuesday
- `left:41.8000%` → Wednesday
- `left:61.2000%` → Thursday
- `left:80.6000%` → Friday

### Parsed Event Object

After parsing, each event becomes a JSON object:

```json
{
  "date": "11/17/2025",
  "course": "Entrepots de données (Datamart)",
  "professor": "causeur yann",
  "group": "CC MASTERE 1 CYBER + INFRA + ECDPIA + EID 25/26",
  "time": "10:00 - 12:00",
  "room": "201-EPSI(ST EXUPERY)",
  "mode": "Présenciel",
  "color": "rgb(221, 221, 255)",
  "teams_links": [
    {
      "url": "https://teams.microsoft.com/...",
      "type": "MTeams_PRINCIPAL"
    }
  ]
}
```

### Field Descriptions

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `date` | String | Event date (MM/DD/YYYY) | `"11/17/2025"` |
| `course` | String | Course/event name | `"Data Management"` |
| `professor` | String | Professor/instructor name | `"causeur yann"` |
| `group` | String | Student group identifier | `"CC MASTERE 1..."` |
| `time` | String | Time range (HH:MM - HH:MM) | `"09:00 - 12:30"` |
| `room` | String | Room/location name | `"201-EPSI(ST EXUPERY)"` |
| `mode` | String | Attendance mode | `"Présenciel"` or `"Distanciel"` |
| `color` | String | Event background color (RGB) | `"rgb(221, 221, 255)"` |
| `teams_links` | Array | Microsoft Teams meeting links | `[{url, type}]` |

---

## Code Examples

### 1. Automated Login (Selenium)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login_to_wigor(username, password):
    """
    Authenticate with WigorServices and return cookies.
    
    Args:
        username: WigorServices username
        password: User password
        
    Returns:
        Dictionary of cookies
    """
    # Setup Chrome driver
    driver = webdriver.Chrome()
    
    try:
        # Navigate to protected resource (triggers redirect)
        # Use the username in the Tel parameter
        driver.get(f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}")
        
        # Wait for login form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "fm1"))
        )
        
        # Fill credentials
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        
        # Submit form
        driver.find_element(By.ID, "submitBtn").click()
        
        # Wait for redirect back to service
        WebDriverWait(driver, 10).until(
            lambda d: "ws-edt-cd.wigorservices.net" in d.current_url
        )
        
        # Extract cookies
        cookies = {}
        for cookie in driver.get_cookies():
            cookies[cookie['name']] = cookie['value']
        
        return cookies
        
    finally:
        driver.quit()
```

### 2. Fetch Schedule with Cookies

```python
import requests
from datetime import datetime

def fetch_schedule(cookies, username, date=None):
    """
    Fetch schedule HTML for a given date.
    
    Args:
        cookies: Dictionary with ASP.NET_SessionId and .DotNetCasClientAuth
        username: User's username (must match logged-in user)
        date: Date string (MM/DD/YYYY), defaults to today
        
    Returns:
        HTML content as string
    """
    if date is None:
        date = datetime.now().strftime('%m/%d/%Y')
    
    # Tel parameter must match the authenticated username
    url = f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date={date}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    
    response = requests.get(url, headers=headers, cookies=cookies)
    response.raise_for_status()
    
    return response.text
```

### 3. Parse Events from HTML

```python
from bs4 import BeautifulSoup
import re

def parse_events(html):
    """
    Parse events from schedule HTML.
    
    Args:
        html: HTML content string
        
    Returns:
        List of event dictionaries
    """
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    
    # Extract day positions and dates
    day_headers = {}
    for jour_div in soup.find_all('div', class_='Jour'):
        style = jour_div.get('style', '')
        left_match = re.search(r'left:([\d.]+)%', style)
        
        if left_match:
            left_pos = float(left_match.group(1))
            tcjour = jour_div.find('td', class_='TCJour')
            
            if tcjour:
                day_text = tcjour.get_text(strip=True)
                # Parse "Lundi 17 Novembre"
                date_match = re.search(r'(\d+)\s+(\w+)', day_text)
                
                if date_match:
                    day = int(date_match.group(1))
                    month_name = date_match.group(2).lower()
                    
                    # Map month name to number
                    months = {'janvier': 1, 'février': 2, 'mars': 3, 'avril': 4,
                             'mai': 5, 'juin': 6, 'juillet': 7, 'août': 8,
                             'septembre': 9, 'octobre': 10, 'novembre': 11, 'décembre': 12}
                    
                    if month_name in months:
                        month = months[month_name]
                        year = datetime.now().year
                        date = datetime(year, month, day).strftime('%m/%d/%Y')
                        day_headers[left_pos] = date
    
    # Extract events
    for case in soup.find_all('div', class_='Case'):
        table = case.find('table', class_='TCase')
        if not table:
            continue
        
        event = {}
        
        # Get date from position
        style = case.get('style', '')
        left_match = re.search(r'left:([\d.]+)%', style)
        if left_match:
            event_left = float(left_match.group(1))
            # Find closest day
            closest_day = min(day_headers.keys(), key=lambda x: abs(x - event_left))
            event['date'] = day_headers[closest_day]
        
        # Extract fields
        course_cell = table.find('td', class_='TCase')
        if course_cell:
            event['course'] = course_cell.get_text(strip=True)
        
        prof_cell = table.find('td', class_='TCProf')
        if prof_cell:
            text_parts = prof_cell.get_text('\n', strip=True).split('\n')
            if len(text_parts) > 0:
                event['professor'] = text_parts[0]
            if len(text_parts) > 1:
                event['group'] = text_parts[1]
        
        time_cell = table.find('td', class_='TChdeb')
        if time_cell:
            event['time'] = time_cell.get_text(strip=True)
        
        room_cell = table.find('td', class_='TCSalle')
        if room_cell:
            event['room'] = room_cell.get_text(strip=True).replace('Salle:', '').strip()
        
        if 'course' in event:
            events.append(event)
    
    return events
```

### 4. Complete Integration Example

```python
def get_weekly_schedule(username, password):
    """
    Complete workflow: login, fetch, and parse schedule.
    
    Args:
        username: WigorServices username
        password: User password
        
    Returns:
        List of event dictionaries
    """
    # Step 1: Login and get cookies
    cookies = login_to_wigor(username, password)
    
    # Step 2: Fetch schedule HTML (pass username for Tel parameter)
    html = fetch_schedule(cookies, username)
    
    # Step 3: Parse events
    events = parse_events(html)
    
    return events

# Usage
events = get_weekly_schedule("john.doe", "your_password")

for event in events:
    print(f"{event['date']} - {event['course']} at {event['time']}")

for event in events:
    print(f"{event['date']} - {event['course']} at {event['time']}")
```

---

## Integration Guide

### Building a Mobile App

#### React Native Example

```javascript
// API Service
class WigorService {
  constructor() {
    this.cookies = null;
  }

  async login(username, password) {
    // Use react-native-webview to handle CAS login
    // Or implement headless browser approach
    // Store cookies after successful login
  }

  async fetchSchedule(date) {
    const url = `https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=${username}&date=${date}`;
    
    const response = await fetch(url, {
      headers: {
        'Cookie': this.cookies,
        'User-Agent': 'Mozilla/5.0...'
      }
    });
    
    return await response.text();
  }

  parseEvents(html) {
    // Use cheerio or similar HTML parser
    // Return parsed event objects
  }
}
```

### Building a Web App

#### Express.js Backend

```javascript
const express = require('express');
const puppeteer = require('puppeteer');
const cheerio = require('cheerio');

const app = express();

// Login endpoint
app.post('/api/login', async (req, res) => {
  const { username, password } = req.body;
  
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  try {
    // Navigate and login
    await page.goto('https://ws-edt-cd.wigorservices.net/...');
    await page.waitForSelector('#username');
    
    await page.type('#username', username);
    await page.type('#password', password);
    await page.click('#submitBtn');
    
    await page.waitForNavigation();
    
    // Extract cookies
    const cookies = await page.cookies();
    
    res.json({ cookies });
  } finally {
    await browser.close();
  }
});

// Schedule endpoint
app.get('/api/schedule', async (req, res) => {
  const { cookies, date } = req.query;
  
  // Fetch and parse schedule
  // Return JSON events
});
```

### Building a Desktop App

#### Electron Example

```javascript
const { BrowserWindow } = require('electron');
const axios = require('axios');

class ScheduleManager {
  async authenticate(username, password) {
    // Create hidden browser window for CAS login
    const win = new BrowserWindow({
      show: false,
      webPreferences: {
        nodeIntegration: false
      }
    });
    
    win.loadURL('https://cas-p.wigorservices.net/cas/login?service=...');
    
    // Inject login script
    await win.webContents.executeJavaScript(`
      document.getElementById('username').value = '${username}';
      document.getElementById('password').value = '${password}';
      document.getElementById('submitBtn').click();
    `);
    
    // Wait for redirect
    await new Promise(resolve => {
      win.webContents.on('did-navigate', (event, url) => {
        if (url.includes('ws-edt-cd.wigorservices.net')) {
          resolve();
        }
      });
    });
    
    // Get cookies
    const cookies = await win.webContents.session.cookies.get({});
    win.close();
    
    return cookies;
  }
}
```

### API Rate Limiting

**Recommendations:**
- Max 1 request per minute to avoid detection
- Cache schedule data for 1 hour
- Refresh cookies every 30 minutes
- Use exponential backoff on errors

### Error Handling

```python
def fetch_with_retry(url, cookies, max_retries=3):
    """Fetch with automatic retry and cookie refresh"""
    for attempt in range(max_retries):
        try:
            response = requests.get(url, cookies=cookies)
            
            # Check if redirected to login (cookies expired)
            if 'cas' in response.url and 'login' in response.url:
                # Cookies expired, need to re-authenticate
                raise CookieExpiredError("Session expired")
            
            response.raise_for_status()
            return response.text
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

---

## Security Considerations

### 1. Credential Storage
- **Never** hardcode credentials
- Use secure storage (keychain, encrypted storage)
- Implement credential encryption at rest

### 2. Cookie Management
- Store cookies securely
- Encrypt cookie values
- Clear cookies on logout
- Implement automatic cookie refresh

### 3. HTTPS Only
- Always use HTTPS for requests
- Verify SSL certificates
- Implement certificate pinning (mobile apps)

### 4. Rate Limiting
- Respect server resources
- Implement client-side throttling
- Cache responses appropriately

### 5. User Privacy
- Don't log sensitive data (passwords, cookies)
- Implement proper session timeout
- Clear sensitive data from memory

---

## Troubleshooting

### Common Issues

**1. Authentication Fails**
```
Error: Redirected to login page
Solution: Cookies expired, need to re-authenticate
```

**2. No Events Returned**
```
Error: Empty events array
Solution: Check date format (MM/DD/YYYY), verify cookies valid
```

**3. Parsing Errors**
```
Error: Cannot parse event data
Solution: HTML structure may have changed, update selectors
```

**4. Rate Limited**
```
Error: HTTP 429 or slow responses
Solution: Implement request throttling, add delays
```

---

## Additional Resources

### HTML Class Reference

| Class | Purpose | Example |
|-------|---------|---------|
| `.Case` | Event container | Main event div |
| `.TCase` | Table/cell | Event details table |
| `.Jour` | Day header | Day name and date |
| `.TCJour` | Day cell | Contains day text |
| `.TCProf` | Professor cell | Prof name and group |
| `.TChdeb` | Time cell | Start/end time |
| `.TCSalle` | Room cell | Room location |
| `.Teams` | Teams div | Meeting links |

### CSS Selectors

```css
/* All events */
div.Case

/* Event with specific position */
div.Case[style*="left:22.4000%"]

/* Day headers */
div.Jour td.TCJour

/* Course names */
table.TCase td.TCase

/* Time ranges */
td.TChdeb
```

---

## License & Legal

**Important:** This documentation is for educational purposes. Always respect:
- WigorServices Terms of Service
- Rate limiting and fair use
- User privacy and data protection
- Applicable laws and regulations

**Disclaimer:** Automated access may be against Terms of Service. Use responsibly and at your own risk.

---

## Changelog

**v1.0.0 (2025-11-18)**
- Initial documentation
- Complete authentication flow
- Event parsing guide
- Integration examples

---

**Questions or Issues?**

See the main project README or create an issue in the repository.

