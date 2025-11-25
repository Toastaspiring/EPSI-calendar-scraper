document.addEventListener('DOMContentLoaded', () => {
    // State
    let events = [];
    let currentDate = new Date();

    // UI Elements
    const loginView = document.getElementById('login-view');
    const manualView = document.getElementById('manual-view');
    const appView = document.getElementById('app-view');
    const loginForm = document.getElementById('login-form');
    const errorMsg = document.getElementById('error-msg');
    const loading = document.getElementById('loading');

    // Config
    const START_HOUR = 7;
    const END_HOUR = 21;
    const HOUR_HEIGHT = 60;

    // --- Navigation ---

    document.getElementById('manual-btn').addEventListener('click', () => {
        loginView.style.display = 'none';
        manualView.style.display = 'block';
    });

    document.getElementById('back-btn').addEventListener('click', () => {
        manualView.style.display = 'none';
        loginView.style.display = 'block';
    });

    document.getElementById('logout-btn').addEventListener('click', () => {
        appView.style.display = 'none';
        loginView.style.display = 'block';
        events = [];
        loginForm.reset();
    });

    // --- Login Logic ---

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const url = document.getElementById('url').value;
        const proxy = document.getElementById('proxy').value;

        showLoading(true);
        errorMsg.style.display = 'none';

        try {
            const html = await performLogin(username, password, url, proxy);
            events = extractEvents(html);

            // Allow empty events (e.g. holiday week), but warn
            if (events.length === 0) {
                console.warn("No events found.");
            }

            initApp();
        } catch (err) {
            console.error(err);
            errorMsg.textContent = err.message;
            errorMsg.style.display = 'block';
        } finally {
            showLoading(false);
        }
    });

    document.getElementById('parse-btn').addEventListener('click', () => {
        const html = document.getElementById('html-source').value;
        try {
            console.log("Parsing pasted HTML...");
            events = extractEvents(html);
            console.log("Found events:", events.length);
            if (events.length === 0) {
                alert("No events found in the pasted HTML. Opening empty calendar.");
            }
            initApp();
            manualView.style.display = 'none';
        } catch (e) {
            console.error(e);
            alert("Error parsing HTML: " + e.message);
        }
    });

    function showLoading(show) {
        loading.style.display = show ? 'block' : 'none';
        document.getElementById('loginBtn').disabled = show;
    }

    async function performLogin(username, password, targetUrl, proxyUrl) {
        const fetchUrl = (u) => proxyUrl ? proxyUrl + encodeURIComponent(u) : u;

        console.log("Fetching login page via proxy...");
        const resp1 = await fetch(fetchUrl(targetUrl));
        const page1 = await resp1.text();

        if (page1.includes('class="Jour"')) {
            return page1;
        }

        const parser = new DOMParser();
        const doc = parser.parseFromString(page1, 'text/html');

        const lt = doc.querySelector('input[name="lt"]')?.value;
        const execution = doc.querySelector('input[name="execution"]')?.value;
        const formAction = doc.querySelector('form')?.action;

        if (!lt || !execution) {
            throw new Error("Could not find login form fields. Are you already logged in or is the proxy blocked?");
        }

        let actionUrl = "https://cas-p.wigorservices.net" + (formAction.startsWith('/') ? formAction : '/' + formAction);
        if (formAction.startsWith('http')) actionUrl = formAction;

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('lt', lt);
        formData.append('execution', execution);
        formData.append('_eventId', 'submit');

        console.log("Submitting credentials to", actionUrl);

        const resp2 = await fetch(fetchUrl(actionUrl), {
            method: 'POST',
            body: formData,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        const page2 = await resp2.text();

        if (page2.includes('class="Jour"')) {
            return page2;
        } else if (page2.includes('Touche Verr. Maj.')) {
             throw new Error("Invalid credentials.");
        } else {
            if (page2.includes('action="')) {
                throw new Error("Login failed (returned to login page). Check credentials.");
            }
            throw new Error("Login successful but failed to load schedule. (Unknown page content)");
        }
    }

    function extractEvents(htmlStr) {
        const parser = new DOMParser();
        const doc = parser.parseFromString(htmlStr, 'text/html');
        const events = [];

        const dayHeaders = {};
        const jourDivs = doc.querySelectorAll('div.Jour');

        const frenchMonths = {
            'janvier': 0, 'février': 1, 'mars': 2, 'avril': 3,
            'mai': 4, 'juin': 5, 'juillet': 6, 'août': 7,
            'septembre': 8, 'octobre': 9, 'novembre': 10, 'décembre': 11
        };

        jourDivs.forEach(div => {
            const style = div.getAttribute('style') || '';
            console.log("Checking Jour div style:", style);
            // Robust regex for left position
            const leftMatch = style.match(/left\s*:\s*([\d.]+)%/);
            if (leftMatch) {
                const leftPos = parseFloat(leftMatch[1]);
                const tcjour = div.querySelector('.TCJour');
                if (tcjour) {
                    const text = tcjour.textContent.trim();
                    console.log("Found TCJour text:", text);
                    const dateMatch = text.match(/(\d+)\s+([a-zA-Z\u00C0-\u00FF]+)/);
                    if (dateMatch) {
                        const dayNum = parseInt(dateMatch[1]);
                        const monthName = dateMatch[2].toLowerCase();
                        console.log("Parsed date:", dayNum, monthName);
                        if (monthName in frenchMonths) {
                            const monthIndex = frenchMonths[monthName];
                            const year = 2025;
                            const date = new Date(year, monthIndex, dayNum);
                            dayHeaders[leftPos] = date;
                        } else {
                            console.warn("Month not found:", monthName);
                        }
                    } else {
                        console.warn("Date regex mismatch for:", text);
                    }
                }
            } else {
                console.warn("Left position not found in style:", style);
            }
        });

        console.log("Found day headers:", dayHeaders);

        const caseDivs = doc.querySelectorAll('div.Case');
        caseDivs.forEach(div => {
            if (div.id === 'Apres') return;

            const table = div.querySelector('table.TCase');
            if (!table) return;

            const evt = {};

            const style = div.getAttribute('style') || '';
            const leftMatch = style.match(/left\s*:\s*([\d.]+)%/);
            if (leftMatch) {
                const leftPos = parseFloat(leftMatch[1]);
                let closestDate = null;
                let minDiff = Infinity;

                for (const pos in dayHeaders) {
                    const diff = Math.abs(leftPos - parseFloat(pos));
                    if (diff < minDiff) {
                        minDiff = diff;
                        closestDate = dayHeaders[pos];
                    }
                }
                evt.dateObj = closestDate;
            }

            if (style.includes('background-color')) {
                // Robust color extraction
                const bgMatch = style.match(/background-color\s*:\s*([^;]+)/);
                if (bgMatch) evt.color = bgMatch[1].trim();
            }

            const courseCell = table.querySelector('td.TCase');
            if (courseCell) {
                const clone = courseCell.cloneNode(true);
                clone.querySelectorAll('div').forEach(e => e.remove());
                evt.course = clone.textContent.trim();
            }

            const profCell = table.querySelector('td.TCProf');
            if (profCell) {
                const text = profCell.textContent.trim().split('\n');
                if (text.length > 0) evt.professor = text[0].trim();
                if (text.length > 1) evt.group = text[1].trim();
                const img = profCell.querySelector('img');
                if (img) evt.mode = img.title || img.alt;
            }

            const timeCell = table.querySelector('td.TChdeb');
            if (timeCell) {
                evt.time = timeCell.textContent.trim();
                const [start, end] = evt.time.split(' - ');
                evt.start = parseTime(start);
                evt.end = parseTime(end);
            }

            const roomCell = table.querySelector('td.TCSalle');
            if (roomCell) {
                evt.room = roomCell.textContent.replace('Salle:', '').trim();
            }

            if (evt.course && evt.dateObj) {
                events.push(evt);
            }
        });

        return events;
    }

    function initApp() {
        console.log("Initializing App with events:", events);
        loginView.style.display = 'none';
        appView.style.display = 'flex';

        if (events.length > 0) {
            const sorted = [...events].sort((a, b) => a.dateObj - b.dateObj);
            const todayStr = new Date().toDateString();
            const hasToday = events.some(e => e.dateObj.toDateString() === todayStr);
            currentDate = hasToday ? new Date() : sorted[0].dateObj;
        }

        initGrid();
        renderDay(currentDate);
    }

    const timeCol = document.querySelector('.time-column');
    const gridLines = document.getElementById('grid-lines');
    const eventsContainer = document.getElementById('events-container');
    const currentDateEl = document.getElementById('current-date');

    document.getElementById('prev-day').addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() - 1);
        renderDay(currentDate);
    });

    document.getElementById('next-day').addEventListener('click', () => {
        currentDate.setDate(currentDate.getDate() + 1);
        renderDay(currentDate);
    });

    document.getElementById('today-btn').addEventListener('click', () => {
        currentDate = new Date();
        renderDay(currentDate);
    });

    function initGrid() {
        timeCol.innerHTML = '';
        gridLines.innerHTML = '';

        for (let i = START_HOUR; i <= END_HOUR; i++) {
            const timeSlot = document.createElement('div');
            timeSlot.className = 'time-slot';
            timeSlot.textContent = `${i}:00`;
            timeCol.appendChild(timeSlot);

            const line = document.createElement('div');
            line.className = 'grid-line';
            gridLines.appendChild(line);
        }
    }

    function renderDay(date) {
        const options = { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' };
        currentDateEl.textContent = date.toLocaleDateString('en-US', options);

        const existingCards = eventsContainer.querySelectorAll('.event-card');
        existingCards.forEach(el => el.remove());

        const dayEvents = events.filter(e => isSameDay(e.dateObj, date));

        dayEvents.forEach(evt => {
            const card = document.createElement('div');
            card.className = 'event-card';

            const startH = evt.start.hours + evt.start.minutes / 60;
            const endH = evt.end.hours + evt.end.minutes / 60;
            const duration = endH - startH;

            const top = (startH - START_HOUR) * HOUR_HEIGHT;
            const height = duration * HOUR_HEIGHT;

            card.style.top = `${top}px`;
            card.style.height = `${height}px`;
            card.style.backgroundColor = evt.color || '#1a73e8';

            card.innerHTML = `
                <div class="event-title">${evt.course}</div>
                <div class="event-time">${evt.time}</div>
                <div class="event-location">${evt.room || ''}</div>
                <div>${evt.professor || ''}</div>
            `;

            eventsContainer.appendChild(card);
        });
    }

    function parseTime(timeStr) {
        if (!timeStr) return { hours: 0, minutes: 0 };
        const [h, m] = timeStr.split(':').map(Number);
        return { hours: h, minutes: m };
    }

    function isSameDay(d1, d2) {
        return d1.getFullYear() === d2.getFullYear() &&
               d1.getMonth() === d2.getMonth() &&
               d1.getDate() === d2.getDate();
    }
});
