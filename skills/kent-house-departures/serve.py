#!/usr/bin/env python3
"""Simple HTTP server to serve the departure board"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 8080
DIRECTORY = "/data/.openclaw/workspace/skills/kent-house-departures"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add CORS and no-cache headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

def main():
    index_file = os.path.join(DIRECTORY, "departure_board.html")
    
    if not os.path.exists(index_file):
        print("⚠️  departure_board.html not found!")
        print("   Run: python3 fetch_departures.py")
        return
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        url = f"http://localhost:{PORT}/departure_board.html"
        print(f"🚆 Kent House Departure Board")
        print(f"🌐 Serving at: {url}")
        print(f"📁 Directory: {DIRECTORY}")
        print(f"\nPress Ctrl+C to stop")
        
        # Try to open browser
        try:
            webbrowser.open(url)
        except:
            pass
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Server stopped")

if __name__ == "__main__":
    main()
