import os
import smtplib
from email.mime.text import MIMEText
from playwright.sync_api import sync_playwright
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
    print("Email sent successfully!")

# ===========================
# John Pennekamp availability check
# ===========================
TARGET_DATE = "04/04/2026"
URL = "https://www.floridastateparks.org/stay-night"

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL)

        # Click "Book your overnight stay today"
        page.click("a:has-text('Book your overnight stay today')")

        # Wait for search input to appear
        page.wait_for_selector("#home-search-location-input", timeout=15000)

        # Enter park name and press Enter
        page.fill("#home-search-location-input", "John Pennekamp Coral Reef State Park")
        page.keyboard.press("Enter")

        # Set arrival date
        page.fill("#arrivaldate", TARGET_DATE)

        # Nights = 1
        page.fill("#nights", "1")

        # Click "Show Results"
        page.click("button:has-text('Show Results')")

        # Wait for results page to load
        page.wait_for_selector(f"a[aria-label*='John Pennekamp Coral Reef State Park']", timeout=15000)

        park_card = page.query_selector(f"a[aria-label*='John Pennekamp Coral Reef State Park']")
        label = park_card.get_attribute("aria-label") if park_card else None

        match = re.search(r'(\d+)\s+sites', label) if label else None
        available_sites = int(match.group(1)) if match else 0

        # CST timestamp
        now_cst = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %I:%M:%S %p CST")

        if available_sites > 0:
            subject = f"🚨 John Pennekamp Available: {available_sites} sites!"
            body = f"Availability detected!\n\n{available_sites} sites available at John Pennekamp Coral Reef State Park for April 4-5, 2026.\n\nChecked at {now_cst}"
            send_email(subject, body)
        else:
            print(f"No availability (0 sites) as of {now_cst}")

        browser.close()

except Exception as e:
    now_cst = datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%d %I:%M:%S %p CST")
    send_email(
        "John Pennekamp Script Error",
        f"Something went wrong at {now_cst}:\n{e}"
    )
    raise
