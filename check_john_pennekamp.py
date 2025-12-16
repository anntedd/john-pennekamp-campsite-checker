import os
import time
import re
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================
# Load environment variables
# ==============================
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ==============================
# Email function
# ==============================
def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

# ==============================
# Logging function
# ==============================
def log_result(message):
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    with open(f"logs/log_{timestamp}.txt", "w") as f:
        f.write(message)
    print(message)

# ==============================
# Selenium setup
# ==============================
chrome_options = Options()
chrome_options.add_argument("--headless")  # run without opening a browser window
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 15)

try:
    # ==============================
    # Open reservation page
    # ==============================
    driver.get("https://www.floridastateparks.org/stay-night")

    # Click "Book your overnight stay today!" button
    book_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Book your overnight stay today')]")))
    book_button.click()

    # Wait for new page to load (park search)
    wait.until(EC.presence_of_element_located((By.ID, "home-search-location-input")))

    # ==============================
    # Enter park name
    # ==============================
    park_input = driver.find_element(By.ID, "home-search-location-input")
    park_input.send_keys("John Pennekamp Coral Reef State Park")
    time.sleep(2)  # wait for autocomplete
    park_input.send_keys("\n")

    # ==============================
    # Select arrival date
    # ==============================
    arrival_input = driver.find_element(By.ID, "arrivaldate")
    arrival_input.clear()
    arrival_input.send_keys("04/04/2026")

    # Nights = 1
    nights_input = driver.find_element(By.ID, "nights")
    nights_input.clear()
    nights_input.send_keys("1")

    # Click "Show Results"
    show_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Show Results')]")))
    show_button.click()

    # ==============================
    # Wait for results page
    # ==============================
    park_card = wait.until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@aria-label,'John Pennekamp Coral Reef State Park')]"))
    )

    label = park_card.get_attribute("aria-label")
    match = re.search(r'(\d+)\s+sites', label)
    available_sites = int(match.group(1)) if match else 0

    # ==============================
    # Send email and log
    # ==============================
    if available_sites > 0:
        subject = f"🚨 John Pennekamp Available: {available_sites} sites!"
        body = f"Availability detected!\n\n{available_sites} sites available at John Pennekamp Coral Reef State Park for April 4-5, 2026.\n\nChecked at {datetime.now()}"
        send_email(subject, body)
        log_result(body)
    else:
        # optional: heartbeat email (or just log)
        log_result(f"No availability (0 sites) as of {datetime.now()}")

finally:
    driver.quit()
