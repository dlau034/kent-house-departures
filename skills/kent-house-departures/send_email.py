#!/usr/bin/env python3
"""Send email with HTML attachment via Gmail SMTP"""

import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

CONFIG_FILE = "/data/.openclaw/workspace/skills/kent-house-departures/config.json"

def send_departure_board():
    # Load config
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    sender_email = config['transportApi'].get('email', 'botdino375@gmail.com')
    sender_password = config['transportApi'].get('appPassword', '')
    
    if not sender_password:
        print("❌ Error: Need Gmail app password to send email")
        print("   Add 'email' and 'appPassword' to config.json transportApi section")
        return
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = 'botdino375@gmail.com'
    msg['Subject'] = '🚆 Kent House Live Departures'
    
    body = """Hi!

Attached is your live Kent House Station departure board.

Open the HTML file in any web browser to view live train times.

- OpenClaw
"""
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach HTML file
    html_path = "/data/.openclaw/workspace/skills/kent-house-departures/departure_board.html"
    with open(html_path, 'rb') as f:
        attachment = MIMEBase('application', 'octet-stream')
        attachment.set_payload(f.read())
    
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment; filename="kent_house_departures.html"')
    msg.attach(attachment)
    
    # Send via Gmail SMTP
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email sent to botdino375@gmail.com")
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    send_departure_board()
