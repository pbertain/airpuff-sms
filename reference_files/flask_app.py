# app.py
import os, datetime
from flask import Flask, request, abort
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3

app = Flask(__name__)

TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]  # set in your env
PUBLIC_WEBHOOK_URL = os.environ.get("PUBLIC_WEBHOOK_URL")  # your https webhook base

DB = "subscribers.db"

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def now_iso():
    return datetime.datetime.utcnow().isoformat() + "Z"

def get_sub(phone):
    with db() as conn:
        cur = conn.execute("SELECT * FROM subscribers WHERE phone_e164=?", (phone,))
        return cur.fetchone()

def upsert_sub(phone, status=None, last_keyword=None, consent=False):
    existing = get_sub(phone)
    with db() as conn:
        if existing:
            conn.execute(
                "UPDATE subscribers SET status=COALESCE(?, status), last_keyword=COALESCE(?, last_keyword), updated_at=? , consent_ts=COALESCE(?, consent_ts) WHERE phone_e164=?",
                (status, last_keyword, now_iso(), now_iso() if consent else None, phone),
            )
        else:
            conn.execute(
                "INSERT INTO subscribers(phone_e164,status,created_at,updated_at,last_keyword,consent_ts) VALUES (?,?,?,?,?,?)",
                (phone, status or "pending", now_iso(), now_iso(), last_keyword, now_iso() if consent else None),
            )

def require_twilio_signature():
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = (PUBLIC_WEBHOOK_URL or request.url)  # Prefer configured public URL if set
    if not validator.validate(url, request.form, signature):
        abort(403)

@app.route("/sms/inbound", methods=["POST"])
def sms_inbound():
    require_twilio_signature()

    from_num = request.form.get("From", "")
    body = (request.form.get("Body") or "").strip().upper()

    # Basic keyword routing (Twilio can do Advanced Opt-Out automatically; we still track locally)
    resp = MessagingResponse()

    if body in {"STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"}:
        upsert_sub(from_num, status="unsubscribed", last_keyword=body)
        # When Advanced Opt-Out is enabled, Twilio sends its own compliance message.
        # It's fine to not send an additional message here.
        return str(resp)

    if body in {"START", "YES", "UNSTOP", "JOIN", "SUBSCRIBE"}:
        upsert_sub(from_num, status="subscribed", last_keyword=body, consent=True)
        resp.message("You’re subscribed ✅. Reply STOP to opt out anytime.")
        return str(resp)

    if body in {"HELP", "INFO"}:
        resp.message("Help: Reply JOIN to subscribe, STOP to unsubscribe. Std msg/data rates apply.")
        return str(resp)

    # Regular inbound: check subscription
    sub = get_sub(from_num)
    if not sub or sub["status"] != "subscribed":
        upsert_sub(from_num, status="pending")  # remember them as 'pending'
        resp.message("You’re not subscribed yet. Reply JOIN to opt in. Reply HELP for info.")
        return str(resp)

    # At this point they are subscribed → do your app logic
    resp.message("Thanks! You’re on the list. What can I do for you?")
    return str(resp)

@app.route("/sms/status", methods=["POST"])
def sms_status():
    require_twilio_signature()

    to_num = request.form.get("To")
    status = request.form.get("MessageStatus")               # queued/sent/delivered/failed/undelivered
    err = request.form.get("ErrorCode")                      # e.g., 21610 unsubscribe, 30003 unknown, etc.

    # React to compliance/blocked signals
    if err == "21610":
        # Recipient has opted out from Twilio side → mark locally
        upsert_sub(to_num, status="unsubscribed", last_keyword="STOP(21610)")
    elif status in {"undelivered", "failed"} and err in {"21608", "30003"}:
        # 21608: Permission to send an SMS has not been enabled for the region,
        # 30003: Unreachable/unknown handset, etc. Decide your policy:
        upsert_sub(to_num, status=get_sub(to_num)["status"] or "pending")

    return ("", 204)