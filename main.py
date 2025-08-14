import os
import time
import requests
from threading import Thread
from flask import Flask

# ==== CONFIG (use environment variables in Railway) ====
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BASE_CURRENCY = "GBP"
TARGET_CURRENCY = "NPR"
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # default 60 sec

# Flask app for Railway's web requirement
app = Flask(__name__)

last_rate = None

def get_rate():
    """Fetch GBP→NPR rate from exchangerate.host"""
    url = f"https://api.exchangerate.host/latest?base={BASE_CURRENCY}&symbols={TARGET_CURRENCY}"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    return round(data["rates"][TARGET_CURRENCY], 4)

def send_message(text):
    """Send Telegram message"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})

def rate_checker():
    """Continuously check for rate changes"""
    global last_rate
    while True:
        try:
            rate = get_rate()
            if rate != last_rate:
                msg = f"💱 GBP → NPR: {rate}"
                send_message(msg)
                last_rate = rate
        except Exception as e:
            print("Error:", e)
        time.sleep(CHECK_INTERVAL)

# Start background thread
Thread(target=rate_checker, daemon=True).start()

@app.route("/")
def home():
    return "GBP→NPR Rate Bot is running ✅"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
