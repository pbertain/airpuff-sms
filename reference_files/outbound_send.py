# send.py
import os
import sqlite3
from twilio.rest import Client

def db():
    conn = sqlite3.connect("subscribers.db")
    conn.row_factory = sqlite3.Row
    return conn

def is_subscribed(phone):
    with db() as conn:
        cur = conn.execute("SELECT status FROM subscribers WHERE phone_e164=?", (phone,))
        row = cur.fetchone()
        return row and row["status"] == "subscribed"

def send_sms(to, body):
    if not is_subscribed(to):
        print(f"Skip: {to} not subscribed")
        return

    client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
    msg = client.messages.create(
        to=to,
        from_=os.environ["TWILIO_FROM_NUMBER"],
        body=body,
        status_callback=os.environ.get("PUBLIC_STATUS_URL") or None,  # e.g., https://<your-domain>/sms/status
    )
    print("Queued:", msg.sid)