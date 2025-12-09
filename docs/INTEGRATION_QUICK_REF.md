# Quick Integration Reference

Fast reference for integrating WigorServices schedule into your application.

---

## 🚀 Quick Start

### 1. Authentication (3 steps)

```python
from selenium import webdriver
from selenium.webdriver.common.by import By

def get_cookies(username, password):
    driver = webdriver.Chrome()
    # Use the username in the URL Tel parameter
    driver.get(f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}")
    
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "submitBtn").click()
    
    time.sleep(3)
    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    driver.quit()
    
    return cookies
```

### 2. Fetch Schedule

```python
import requests

def get_schedule(cookies, username, date="11/18/2025"):
    # Tel parameter must match the logged-in username
    url = f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date={date}"
    
    response = requests.get(url, cookies=cookies)
    return response.text
```

### 3. Parse Events

```python
from bs4 import BeautifulSoup

def parse_events(html):
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    
    for case in soup.find_all('div', class_='Case'):
        table = case.find('table', class_='TCase')
        if not table:
            continue
        
        event = {}
        
        # Course name
        course = table.find('td', class_='TCase')
        if course:
            event['course'] = course.get_text(strip=True)
        
        # Time
        time = table.find('td', class_='TChdeb')
        if time:
            event['time'] = time.get_text(strip=True)
        
        # Room
        room = table.find('td', class_='TCSalle')
        if room:
            event['room'] = room.get_text(strip=True).replace('Salle:', '').strip()
        
        if event.get('course'):
            events.append(event)
    
    return events
```

---

## 📋 Essential Endpoints

### Login Endpoint
```
https://cas-p.wigorservices.net/cas/login?service=<encoded_service_url>
```

### Schedule Endpoint
```
https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=<username>&date=<MM/DD/YYYY>
```

**Important:** The `Tel` parameter must be the **same username** used for login.

**Example:**
- User logs in with username: `john.doe`
- Schedule URL: `...&Tel=john.doe&date=11/18/2025`

---

## 🔑 Required Cookies

After login, you need:

```python
cookies = {
    'ASP.NET_SessionId': '<session_id>',
    '.DotNetCasClientAuth': '<auth_token>'
}
```

---

## 📊 Event Object Structure

```json
{
  "date": "11/18/2025",
  "course": "Data Management",
  "professor": "reinette reynholds",
  "group": "CC MASTERE 1 CYBER + INFRA + ECDPIA + EID 25/26",
  "time": "13:30 - 17:30",
  "room": "201-EPSI(ST EXUPERY)",
  "mode": "Présenciel",
  "teams_links": [
    {"url": "https://teams.microsoft.com/...", "type": "PRINCIPAL"}
  ]
}
```

---

## 🎯 Complete Example (Copy-Paste Ready)

```python
#!/usr/bin/env python3
"""
WigorServices Schedule Fetcher
Minimal working example
"""

import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def authenticate(username, password):
    """Login and return cookies"""
    options = Options()
    options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to schedule (will redirect to login)
        driver.get(f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}")
        time.sleep(2)
        
        # Fill login form
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "submitBtn").click()
        
        # Wait for redirect
        time.sleep(3)
        
        # Get cookies
        cookies = {}
        for cookie in driver.get_cookies():
            cookies[cookie['name']] = cookie['value']
        
        return cookies
        
    finally:
        driver.quit()

def fetch_schedule(cookies, username, date):
    """Fetch schedule HTML"""
    url = f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}&date={date}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    response = requests.get(url, headers=headers, cookies=cookies)
    response.raise_for_status()
    
    return response.text

def parse_events(html):
    """Parse events from HTML"""
    soup = BeautifulSoup(html, 'html.parser')
    events = []
    
    for case in soup.find_all('div', class_='Case'):
        table = case.find('table', class_='TCase')
        if not table:
            continue
        
        event = {}
        
        # Extract course name
        course_cell = table.find('td', class_='TCase')
        if course_cell:
            # Remove nested divs
            for div in course_cell.find_all('div'):
                div.decompose()
            event['course'] = course_cell.get_text(strip=True)
        
        # Extract professor and group
        prof_cell = table.find('td', class_='TCProf')
        if prof_cell:
            parts = prof_cell.get_text('\n', strip=True).split('\n')
            if len(parts) > 0:
                event['professor'] = parts[0]
            if len(parts) > 1:
                event['group'] = parts[1]
        
        # Extract time
        time_cell = table.find('td', class_='TChdeb')
        if time_cell:
            event['time'] = time_cell.get_text(strip=True)
        
        # Extract room
        room_cell = table.find('td', class_='TCSalle')
        if room_cell:
            event['room'] = room_cell.get_text(strip=True).replace('Salle:', '').strip()
        
        if event.get('course'):
            events.append(event)
    
    return events

def main():
    """Main execution"""
    USERNAME = "louis.marec"
    PASSWORD = "your_password"
    DATE = "11/18/2025"
    
    print("1. Authenticating...")
    cookies = authenticate(USERNAME, PASSWORD)
    print(f"   ✓ Got cookies: {list(cookies.keys())}")
    
    print("\n2. Fetching schedule...")
    html = fetch_schedule(cookies, USERNAME, DATE)
    print(f"   ✓ Fetched {len(html)} bytes")
    
    print("\n3. Parsing events...")
    events = parse_events(html)
    print(f"   ✓ Found {len(events)} events")
    
    print("\n4. Events:")
    for i, event in enumerate(events, 1):
        print(f"   {i}. {event.get('course', 'N/A')}")
        print(f"      Time: {event.get('time', 'N/A')}")
        print(f"      Room: {event.get('room', 'N/A')}")
        print()

if __name__ == '__main__':
    main()
```

**Usage:**
```bash
pip install selenium beautifulsoup4 requests
python schedule_fetcher.py
```

---

## 🔧 Framework-Specific Examples

### React/Next.js

```javascript
// app/api/schedule/route.js
export async function POST(request) {
  const { username, password, date } = await request.json();
  
  // Use puppeteer for login
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();
  
  await page.goto('https://cas-p.wigorservices.net/cas/login?service=...');
  await page.type('#username', username);
  await page.type('#password', password);
  await page.click('#submitBtn');
  await page.waitForNavigation();
  
  const cookies = await page.cookies();
  await browser.close();
  
  // Fetch schedule
  const response = await fetch(
    `https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=${username}&date=${date}`,
    { headers: { Cookie: cookies.map(c => `${c.name}=${c.value}`).join('; ') } }
  );
  
  const html = await response.text();
  const events = parseEvents(html);
  
  return Response.json({ events });
}
```

### Flutter/Dart

```dart
import 'package:http/http.dart' as http;
import 'package:html/parser.dart' as html;

class WigorService {
  String? cookies;
  String? username;  // Store username after login
  
  Future<void> login(String username, String password) async {
    // Use webview_flutter or similar for CAS login
    // Store cookies after successful authentication
    this.username = username;  // Save username for later use
  }
  
  Future<List<Event>> fetchSchedule(String date) async {
    // Use the logged-in username in Tel parameter
    final url = 'https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=$username&date=$date';
    
    final response = await http.get(
      Uri.parse(url),
      headers: {'Cookie': cookies!}
    );
    
    final document = html.parse(response.body);
    final events = <Event>[];
    
    for (var case in document.querySelectorAll('div.Case')) {
      final table = case.querySelector('table.TCase');
      if (table == null) continue;
      
      final course = table.querySelector('td.TCase')?.text.trim();
      final time = table.querySelector('td.TChdeb')?.text.trim();
      final room = table.querySelector('td.TCSalle')?.text.trim();
      
      if (course != null) {
        events.add(Event(course: course, time: time, room: room));
      }
    }
    
    return events;
  }
}
```

### Swift/iOS

```swift
import WebKit

class WigorService {
    var cookies: [HTTPCookie] = []
    var username: String?  // Store username after login
    
    func login(username: String, password: String, completion: @escaping (Bool) -> Void) {
        self.username = username  // Save username for later use
        let webView = WKWebView()
        
        // Load CAS login page
        let url = URL(string: "https://cas-p.wigorservices.net/cas/login?service=...")!
        webView.load(URLRequest(url: url))
        
        // Inject JavaScript to fill form
        webView.evaluateJavaScript("""
            document.getElementById('username').value = '\(username)';
            document.getElementById('password').value = '\(password)';
            document.getElementById('submitBtn').click();
        """)
        
        // Monitor navigation
        // Extract cookies on success
        // completion(true)
    }
    
    func fetchSchedule(date: String, completion: @escaping ([Event]) -> Void) {
        guard let username = username else {
            completion([])
            return
        }
        
        // Use the logged-in username in Tel parameter
        let url = URL(string: "https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel=\(username)&date=\(date)")!
        
        var request = URLRequest(url: url)
        request.allHTTPHeaderFields = HTTPCookie.requestHeaderFields(with: cookies)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            guard let data = data, let html = String(data: data, encoding: .utf8) else {
                completion([])
                return
            }
            
            let events = self.parseEvents(html)
            completion(events)
        }.resume()
    }
}
```

---

## ⚠️ Important Notes

### Cookie Lifetime
- Cookies expire after ~1-2 hours
- Re-authenticate when getting login redirect
- Implement automatic cookie refresh

### Rate Limiting
```python
import time

class ThrottledClient:
    def __init__(self):
        self.last_request = 0
        self.min_interval = 1.0  # seconds
    
    def fetch(self, url, cookies):
        # Wait if needed
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        response = requests.get(url, cookies=cookies)
        self.last_request = time.time()
        
        return response
```

### Error Handling
```python
def safe_fetch(cookies):
    try:
        html = fetch_schedule(cookies, date)
        
        # Check if redirected to login
        if '<title>Connexion</title>' in html:
            raise CookieExpiredError()
        
        return html
        
    except CookieExpiredError:
        # Re-authenticate
        cookies = authenticate(username, password)
        return fetch_schedule(cookies, date)
```

---

## 📱 Mobile App Considerations

### Background Sync
```python
# Schedule periodic sync (iOS/Android)
def background_sync():
    cookies = load_cookies()
    
    if cookies_expired(cookies):
        cookies = refresh_cookies()
    
    events = fetch_and_parse(cookies)
    save_to_local_db(events)
    send_notification_if_changes(events)
```

### Offline Support
```python
# Cache events locally
def get_events_with_cache():
    # Try fetching fresh data
    try:
        events = fetch_schedule_online()
        cache_events(events)
        return events
    except:
        # Fallback to cache
        return load_cached_events()
```

---

## 🔍 Debugging

### Check Authentication
```python
def test_auth(cookies, username):
    response = requests.get(
        f"https://ws-edt-cd.wigorservices.net/WebPsDyn.aspx?Action=posEDTLMS&serverID=C&Tel={username}",
        cookies=cookies,
        allow_redirects=False
    )
    
    if response.status_code == 302:
        print("❌ Cookies expired (redirect to login)")
    elif response.status_code == 200:
        print("✓ Cookies valid")
```

### Inspect HTML Structure
```python
def debug_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    print(f"Title: {soup.title.string if soup.title else 'None'}")
    print(f"Day headers: {len(soup.find_all('div', class_='Jour'))}")
    print(f"Events: {len(soup.find_all('div', class_='Case'))}")
    print(f"Tables: {len(soup.find_all('table', class_='TCase'))}")
```

---

## 📚 More Resources

- **Full API Documentation:** `docs/API_DOCUMENTATION.md`
- **Project Repository:** Main README
- **Automated Login:** `docs/AUTO_LOGIN_GUIDE.md`

---

**Ready to integrate?** Copy the complete example above and customize for your needs!

