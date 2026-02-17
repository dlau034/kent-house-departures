#!/usr/bin/env python3
"""Fetch live departures for Kent House Station"""

import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime
import os

CONFIG_FILE = "/data/.openclaw/workspace/skills/kent-house-departures/config.json"
OUTPUT_HTML = "/data/.openclaw/workspace/skills/kent-house-departures/departure_board.html"

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def fetch_transportapi_departures(config):
    """Fetch departures using TransportAPI"""
    app_id = config['transportApi']['appId']
    api_key = config['transportApi']['apiKey']
    station_code = config['stationCode']
    
    if app_id == "YOUR_APP_ID" or api_key == "YOUR_API_KEY":
        return None, "Please configure your TransportAPI credentials in config.json"
    
    # TransportAPI endpoint for live departures (updated)
    url = f"https://transportapi.com/v3/uk/train/station_timetables/{station_code}.json"
    params = f"?app_id={app_id}&app_key={api_key}&live=true"
    
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url + params, method='GET')
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            return parse_transportapi_data(data), None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        return None, f"API Error: {e.code} - {e.reason}. {error_body}"
    except Exception as e:
        return None, f"Error: {str(e)}"

def parse_transportapi_data(data):
    """Parse TransportAPI response into standard format"""
    departures = []
    
    if 'departures' in data and 'all' in data['departures']:
        for dep in data['departures']['all'][:10]:  # Limit to 10
            departures.append({
                'scheduled': dep.get('aimed_departure_time', ''),
                'expected': dep.get('expected_departure_time', dep.get('aimed_departure_time', '')),
                'destination': dep.get('destination_name', 'Unknown'),
                'platform': dep.get('platform', 'TBC'),
                'status': dep.get('status', 'Unknown'),
                'operator': dep.get('operator_name', ''),
                'cancelled': dep.get('status', '').lower() == 'cancelled'
            })
    
    return {
        'station': data.get('station_name', 'Kent House'),
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'departures': departures
    }

def generate_html(data, config):
    """Generate HTML departure board"""
    if not data:
        return generate_error_html("No data available")
    
    station_name = config.get('stationName', 'Kent House')
    refresh_interval = config.get('refreshInterval', 60)
    now_str = data['timestamp']
    
    # Build departure rows
    departure_rows = []
    for dep in data['departures']:
        status_class = 'ontime'
        status_text = 'On Time'
        time_class = ''
        
        if dep['cancelled']:
            status_class = 'cancelled'
            status_text = 'Cancelled'
        elif dep['expected'] != dep['scheduled'] and dep['expected']:
            status_class = 'delayed'
            status_text = f"Exp {dep['expected']}"
            time_class = 'delayed'
        
        row = f'''<div class="departure">
                <div class="time {time_class}">{dep['scheduled']}</div>
                <div class="destination">{dep['destination']}</div>
                <div class="platform">{dep['platform']}</div>
                <div class="status {status_class}">
                    <span class="status-icon {status_class}"></span>
                    {status_text}
                </div>
            </div>'''
        departure_rows.append(row)
    
    departures_html = '\n'.join(departure_rows) if departure_rows else '''
            <div class="empty-state">
                <div class="empty-state-icon">🚫</div>
                <div>No departures found at this time</div>
            </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{station_name} Station - Live Departures</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
        }}
        .header {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .header .subtitle {{
            opacity: 0.8;
            font-size: 14px;
        }}
        .board {{
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }}
        .board-header {{
            background: #003366;
            color: white;
            padding: 16px 20px;
            display: grid;
            grid-template-columns: 80px 1fr 60px 100px;
            gap: 12px;
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .departure {{
            display: grid;
            grid-template-columns: 80px 1fr 60px 100px;
            gap: 12px;
            padding: 16px 20px;
            border-bottom: 1px solid #e0e0e0;
            transition: background 0.2s;
        }}
        .departure:hover {{
            background: #f5f5f5;
        }}
        .departure:last-child {{
            border-bottom: none;
        }}
        .time {{
            font-weight: 700;
            font-size: 18px;
            color: #003366;
        }}
        .time.delayed {{
            color: #e67e22;
        }}
        .destination {{
            font-weight: 500;
            color: #333;
        }}
        .platform {{
            text-align: center;
            font-weight: 700;
            color: #666;
        }}
        .status {{
            text-align: right;
            font-weight: 600;
            font-size: 13px;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 6px;
        }}
        .status.ontime {{
            color: #27ae60;
        }}
        .status.delayed {{
            color: #e67e22;
        }}
        .status.cancelled {{
            color: #e74c3c;
        }}
        .status-icon {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
        }}
        .status-icon.ontime {{
            background: #27ae60;
        }}
        .status-icon.delayed {{
            background: #e67e22;
        }}
        .status-icon.cancelled {{
            background: #e74c3c;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 12px 20px;
            text-align: center;
            color: #666;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .refresh-indicator {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .spinner {{
            width: 12px;
            height: 12px;
            border: 2px solid #ddd;
            border-top-color: #003366;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }}
        @keyframes spin {{
            to {{ transform: rotate(360deg); }}
        }}
        .empty-state {{
            padding: 60px 20px;
            text-align: center;
            color: #666;
        }}
        .empty-state-icon {{
            font-size: 48px;
            margin-bottom: 16px;
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 10px;
            }}
            .header h1 {{
                font-size: 22px;
            }}
            .board-header {{
                display: none;
            }}
            .departure {{
                grid-template-columns: 1fr;
                gap: 8px;
            }}
            .departure > div {{
                display: flex;
                justify-content: space-between;
            }}
            .departure > div::before {{
                font-weight: 600;
                color: #666;
                font-size: 12px;
                text-transform: uppercase;
            }}
            .time::before {{ content: "Time"; }}
            .destination::before {{ content: "Destination"; }}
            .platform::before {{ content: "Platform"; }}
            .status::before {{ content: "Status"; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚆 {station_name}</h1>
            <div class="subtitle">Live Departure Board • Updated {now_str}</div>
        </div>
        
        <div class="board">
            <div class="board-header">
                <div>Time</div>
                <div>Destination</div>
                <div>Plat</div>
                <div>Status</div>
            </div>
{departures_html}
            <div class="footer">
                <div class="refresh-indicator">
                    <div class="spinner"></div>
                    <span>Refreshing in <span id="countdown">{refresh_interval}</span>s</span>
                </div>
                <div>Data provided by TransportAPI</div>
            </div>
        </div>
    </div>
    
    <script>
        let seconds = {refresh_interval};
        const countdownEl = document.getElementById('countdown');
        
        setInterval(() => {{
            seconds--;
            if (seconds <= 0) {{
                window.location.reload();
            }} else {{
                countdownEl.textContent = seconds;
            }}
        }}, 1000);
    </script>
</body>
</html>'''
    return html

def generate_error_html(message):
    return f'''<!DOCTYPE html>
<html>
<head>
    <title>Error - Kent House Departures</title>
    <style>
        body {{ font-family: sans-serif; padding: 40px; text-align: center; }}
        .error {{ color: #e74c3c; }}
    </style>
</head>
<body>
    <h1 class="error">⚠️ Error</h1>
    <p>{message}</p>
    <p>Please check your API configuration in config.json</p>
</body>
</html>'''

def main():
    print("🚆 Fetching Kent House departures...")
    
    config = load_config()
    
    # Fetch data based on configured provider
    provider = config.get('apiProvider', 'transportapi')
    
    if provider == 'transportapi':
        data, error = fetch_transportapi_departures(config)
    else:
        data, error = None, "Unknown API provider"
    
    if error:
        print(f"❌ {error}")
        html = generate_error_html(error)
    else:
        print(f"✅ Found {len(data['departures'])} departures")
        html = generate_html(data, config)
    
    # Write HTML file
    with open(OUTPUT_HTML, 'w') as f:
        f.write(html)
    
    print(f"📄 Generated: {OUTPUT_HTML}")
    print(f"🌐 Open in browser: file://{OUTPUT_HTML}")

if __name__ == "__main__":
    main()
