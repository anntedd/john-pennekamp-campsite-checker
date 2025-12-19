import os
import smtplib
import requests
from email.mime.text import MIMEText
from datetime import datetime
from zoneinfo import ZoneInfo
import re

# ===========================
# Email setup
# ===========================
EMAIL_FROM = os.environ["EMAIL_FROM"]
EMAIL_TO = os.environ["EMAIL_TO"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.send_message(msg)
    print(f"Email sent successfully: {subject}")

# ===========================
# John Pennekamp availability check
# ===========================
TARGET_DATE = "04/04/2026"
SEARCH_URL = (
    "https://www.floridastateparks.org/stay-night?park=John+Pennekamp+Coral+Reef+State+Park"
)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/143.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

try:
    response = requests.get(SEARCH_URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    html = response.text

    # Look for number of sites using regex
    match = re.search(r'(\d+)\s+sites\s+available', html, re.IGNORECASE)
    available_sites = int(match.group(1)) if match else 0

    # CST timestamp
    now_cst = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %I:%M:%S %p CST")

    if available_sites > 0:
        subject = f"🚨 John Pennekamp Available: {available_sites} sites!"
        body = f"Availability detected!\n\n{available_sites} sites available at John Pennekamp Coral Reef State Park for April 4-5, 2026.\n\nChecked at {now_cst}"
        send_email(subject, body)
    else:
        print(f"No availability (0 sites) as of {now_cst}")

except Exception as e:
    now_cst = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %I:%M:%S %p CST")
    send_email(
        "John Pennekamp Script Error",
        f"Something went wrong at {now_cst}:\n{e}"
    )
    raise
