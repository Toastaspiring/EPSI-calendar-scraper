# Student Calendar Viewer

A static web application to view your student schedule.

## Features

- **Responsive Design:** Works on desktop and mobile.
- **Login Integration:** Log in with your student credentials to automatically load your schedule (uses a CORS proxy).
- **Manual Mode:** Paste the HTML source of your schedule page if login fails or for better security.
- **Daily View:** Displays your courses in a clear, time-grid format similar to Google Calendar.
- **Client-Side Only:** No backend required. Can be hosted on GitHub Pages.

## How to Use

### Option 1: Automatic Login
1. Enter your Username and Password.
2. Ensure the Schedule URL is correct.
3. (Optional) Change the CORS Proxy if needed.
4. Click "Login & Load Schedule".

### Option 2: Manual Source
1. Log in to your schedule page in a separate tab.
2. Press `Ctrl+U` (or right-click -> View Page Source).
3. Copy the entire HTML content.
4. In this app, click "Paste HTML Source".
5. Paste the code and click "Load Schedule".

## Hosting

This project is designed to be hosted on GitHub Pages.
1. Go to Settings > Pages.
2. Select the branch containing these files.
3. Save.

## Privacy Note

When using the "Automatic Login" feature, your request is routed through a CORS proxy (default: `corsproxy.io`) to bypass browser security restrictions. **Use "Manual Mode" if you do not trust the proxy.**
