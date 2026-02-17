#!/usr/bin/env python3
"""Generate demo data for testing the departure board"""

import json
from datetime import datetime, timedelta

OUTPUT_HTML = "/data/.openclaw/workspace/skills/kent-house-departures/departure_board.html"

def generate_demo_data():
    now = datetime.now()
    
    departures = [
        {
            'scheduled': (now + timedelta(minutes=8)).strftime('%H:%M'),
            'expected': (now + timedelta(minutes=8)).strftime('%H:%M'),
            'destination': 'London Victoria',
            'platform': '1',
            'cancelled': False
        },
        {
            'scheduled': (now + timedelta(minutes=15)).strftime('%H:%M'),
            'expected': (now + timedelta(minutes=18)).strftime('%H:%M'),
            'destination': 'Orpington',
            'platform': '2',
            'cancelled': False
        },
        {
            'scheduled': (now + timedelta(minutes=22)).strftime('%H:%M'),
            'expected': (now + timedelta(minutes=22)).strftime('%H:%M'),
            'destination': 'London Blackfriars',
            'platform': '1',
            'cancelled': False
        },
        {
            'scheduled': (now + timedelta(minutes=35)).strftime('%H:%M'),
            'expected': (now + timedelta(minutes=35)).strftime('%H:%M'),
            'destination': 'Sevenoaks',
            'platform': '2',
            'cancelled': False
        },
        {
            'scheduled': (now + timedelta(minutes=48)).strftime('%H:%M'),
            'expected': '',
            'destination': 'London Victoria',
            'platform': '1',
            'cancelled': True
        },
        {
            'scheduled': (now + timedelta(minutes=55)).strftime('%H:%M'),
            'expected': (now + timedelta(minutes=55)).strftime('%H:%M'),
            'destination': 'Ashford International',
            'platform': '2',
            'cancelled': False
        },
        {
            'scheduled': (now + timedelta(hours=1, minutes=5)).strftime('%H:%M'),
            'expected': (now + timedelta(hours=1, minutes=5)).strftime('%H:%M'),
            'destination': 'London Charing Cross',
            'platform': '1',
            'cancelled': False
        },
        {
            'scheduled': (now + timedelta(hours=1, minutes=18)).strftime('%H:%M'),
            'expected': (now + timedelta(hours=1, minutes=18)).strftime('%H:%M'),
            'destination': 'Dover Priory',
            'platform': '2',
            'cancelled': False
        }
    ]
    
    return {
        'station': 'Kent House',
        'timestamp': now.strftime('%H:%M:%S'),
        'departures': departures
    }

def generate_html(data):
    now_str = data['timestamp']
    
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kent House Station - Live Departures</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 800px; margin: 0 auto; }
        .header {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        .header h1 { font-size: 28px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px; }
        .header .subtitle { opacity: 0.8; font-size: 14px; }
        .demo-badge { display: inline-block; background: #e74c3c; color: white; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-top: 10px; }
        .board { background: rgba(255, 255, 255, 0.95); border-radius: 16px; overflow: hidden; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); }
        .board-header { background: #003366; color: white; padding: 16px 20px; display: grid; grid-template-columns: 80px 1fr 60px 100px; gap: 12px; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; }
        .departure { display: grid; grid-template-columns: 80px 1fr 60px 100px; gap: 12px; padding: 16px 20px; border-bottom: 1px solid #e0e0e0; transition: background 0.2s; }
        .departure:hover { background: #f5f5f5; }
        .departure:last-child { border-bottom: none; }
        .time { font-weight: 700; font-size: 18px; color: #003366; }
        .time.delayed { color: #e67e22; }
        .destination { font-weight: 500; color: #333; }
        .platform { text-align: center; font-weight: 700; color: #666; }
        .status { text-align: right; font-weight: 600; font-size: 13px; display: flex; align-items: center; justify-content: flex-end; gap: 6px; }
        .status.ontime { color: #27ae60; }
        .status.delayed { color: #e67e22; }
        .status.cancelled { color: #e74c3c; }
        .status-icon { width: 8px; height: 8px; border-radius: 50%; }
        .status-icon.ontime { background: #27ae60; }
        .status-icon.delayed { background: #e67e22; }
        .status-icon.cancelled { background: #e74c3c; }
        .footer { background: #f8f9fa; padding: 12px 20px; text-align: center; color: #666; font-size: 12px; display: flex; justify-content: space-between; align-items: center; }
        .refresh-indicator { display: flex; align-items: center; gap: 8px; }
        .spinner { width: 12px; height: 12px; border: 2px solid #ddd; border-top-color: #003366; border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        .setup-info { background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px; margin-bottom: 20px; color: #856404; }
        .setup-info h3 { margin-bottom: 10px; }
        .setup-info code { background: rgba(0,0,0,0.1); padding: 2px 6px; border-radius: 4px; font-family: monospace; }
        @media (max-width: 600px) {
            body { padding: 10px; }
            .header h1 { font-size: 22px; }
            .board-header { display: none; }
            .departure { grid-template-columns: 1fr; gap: 8px; }
            .departure > div { display: flex; justify-content: space-between; }
            .departure > div::before { font-weight: 600; color: #666; font-size: 12px; text-transform: uppercase; }
            .time::before { content: "Time"; }
            .destination::before { content: "Destination"; }
            .platform::before { content: "Platform"; }
            .status::before { content: "Status"; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="setup-info">
            <h3>⚠️ Demo Mode</h3>
            <p>This is sample data. To get live departures:</p>
            <ol style="margin-left: 20px; margin-top: 10px;">
                <li>Sign up at <a href="https://transportapi.com" target="_blank">transportapi.com</a></li>
                <li>Get your free App ID and API Key</li>
                <li>Edit <code>config.json</code> with your credentials</li>
                <li>Run <code>python3 fetch_departures.py</code></li>
            </ol>
        </div>

        <div class="header">
            <h1>🚆 Kent House</h1>
            <div class="subtitle">Live Departure Board • Updated """ + now_str + """</div>
            <div class="demo-badge">DEMO DATA</div>
        </div>
        
        <div class="board">
            <div class="board-header">
                <div>Time</div>
                <div>Destination</div>
                <div>Plat</div>
                <div>Status</div>
            </div>
""")
    
    for dep in data['departures']:
        status_class = 'cancelled' if dep['cancelled'] else ('delayed' if dep['expected'] != dep['scheduled'] else 'ontime')
        status_text = 'Cancelled' if dep['cancelled'] else ('Exp ' + dep['expected'] if dep['expected'] != dep['scheduled'] else 'On Time')
        time_class = 'delayed' if dep['expected'] != dep['scheduled'] and not dep['cancelled'] else ''
        
        html_parts.append(f"""
            <div class="departure">
                <div class="time {time_class}">{dep['scheduled']}</div>
                <div class="destination">{dep['destination']}</div>
                <div class="platform">{dep['platform']}</div>
                <div class="status {status_class}">
                    <span class="status-icon {status_class}"></span>
                    {status_text}
                </div>
            </div>
""")
    
    html_parts.append("""
            <div class="footer">
                <div class="refresh-indicator">
                    <div class="spinner"></div>
                    <span>Refreshing in <span id="countdown">60</span>s</span>
                </div>
                <div>Sample data - Sign up at transportapi.com</div>
            </div>
        </div>
    </div>
    
    <script>
        let seconds = 60;
        const countdownEl = document.getElementById('countdown');
        setInterval(() => {
            seconds--;
            if (seconds <= 0) {
                window.location.reload();
            } else {
                countdownEl.textContent = seconds;
            }
        }, 1000);
    </script>
</body>
</html>
""")
    
    return ''.join(html_parts)

def main():
    print("🚆 Generating DEMO departure board for Kent House Station...")
    data = generate_demo_data()
    html = generate_html(data)
    
    with open(OUTPUT_HTML, 'w') as f:
        f.write(html)
    
    print(f"✅ Generated demo board with {len(data['departures'])} departures")
    print(f"📄 File: {OUTPUT_HTML}")
    print(f"\n🌐 To view:")
    print(f"   python3 serve.py")
    print(f"   or open file://{OUTPUT_HTML}")

if __name__ == "__main__":
    main()
