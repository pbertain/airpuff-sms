import os
import time
import logging
from flask import Flask, request, g
from lib import airpuff_lib
from lib.db_utils import init_database, get_subscriber, upsert_subscriber, is_subscribed
from lib.twilio_utils import TwilioUtils
from twilio.twiml.messaging_response import MessagingResponse
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Script version
__version__ = "7"

app = Flask(__name__)

# Initialize Twilio utilities
try:
    twilio_utils = TwilioUtils()
    logging.info("Twilio utilities initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize Twilio utilities: {e}")
    twilio_utils = None

# Initialize database
try:
    init_database()
    logging.info("Database initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize database: {e}")

# Ensure the log directory exists
log_directory = "/var/log/airpuff-sms"
os.makedirs(log_directory, exist_ok=True)

# Set up logging
log_file = os.path.join(log_directory, "access.log")
handler = RotatingFileHandler(log_file, maxBytes=10000000, backupCount=5)
logging.basicConfig(level=logging.INFO, handlers=[handler], format='%(asctime)s - %(message)s')

@app.before_request
def start_timer():
    g.start_time = time.time()

@app.after_request
def log_request(response):
    response_time = time.time() - g.start_time
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    user_agent = request.headers.get('User-Agent', 'Unknown')

    log_data = {
        "ip": client_ip,
        "status_code": response.status_code,
        "request_data": request.values.get('Body', ''),
        "user_agent": user_agent,
        "response_time": round(response_time, 4)
    }
    log_message = (
        f"{log_data['ip']} {log_data['status_code']} \"{log_data['request_data']}\" "
        f"{log_data['response_time']}s \"{log_data['user_agent']}\""
    )
    app.logger.info(log_message)
    return response

@app.route("/sms/inbound", methods=["POST"])
def sms_inbound():
    """Main SMS webhook endpoint for Twilio"""
    try:
        # Validate Twilio signature for security
        if twilio_utils:
            twilio_utils.validate_signature()
        
        from_num = request.form.get("From", "")
        body = (request.form.get("Body") or "").strip().upper()
        
        app.logger.info(f"Received SMS from {from_num}: {body}")
        
        resp = MessagingResponse()
        
        # Handle compliance keywords (STOP/START)
        if body in {"STOP", "STOPALL", "UNSUBSCRIBE", "CANCEL", "END", "QUIT"}:
            upsert_subscriber(from_num, status="unsubscribed", last_keyword=body)
            # Twilio handles compliance messages automatically when Advanced Opt-Out is enabled
            return str(resp)
        
        if body in {"START", "YES", "UNSTOP", "JOIN", "SUBSCRIBE"}:
            upsert_subscriber(from_num, status="subscribed", last_keyword=body, consent=True)
            resp.message("You're subscribed ✅. Reply STOP to opt out anytime.")
            return str(resp)
        
        if body in {"HELP", "INFO"}:
            resp.message("Help: Reply JOIN to subscribe, STOP to unsubscribe. Std msg/data rates apply.")
            return str(resp)
        
        # Check subscription status for regular messages
        if not is_subscribed(from_num):
            upsert_subscriber(from_num, status="pending")
            resp.message("You're not subscribed yet. Reply JOIN to opt in. Reply HELP for info.")
            return str(resp)
        
        # Process weather requests for subscribed users
        try:
            codes = body.split()[:5]  # Limit to 5 codes max
            responses = []
            
            for code in codes:
                if len(code) <= 4:
                    responses.append(airpuff_lib.get_wx(code))
                else:
                    responses.append(f"{code.upper()}: Not a valid airport code.")
            
            sms_resp_body = "AirPuff:\n" + "\n".join(responses)
            
        except Exception as e:
            app.logger.error(f"Error processing weather request: {str(e)}")
            sms_resp_body = "Sorry, something went wrong while processing your weather request."
        
        resp.message(sms_resp_body)
        return str(resp)
        
    except Exception as e:
        app.logger.error(f"Error in SMS inbound handler: {str(e)}")
        resp = MessagingResponse()
        resp.message("Sorry, something went wrong. Please try again later.")
        return str(resp)

@app.route("/sms/status", methods=["POST"])
def sms_status():
    """Status callback endpoint for outbound message delivery tracking"""
    try:
        # Validate Twilio signature
        if twilio_utils:
            twilio_utils.validate_signature()
        
        to_num = request.form.get("To")
        status = request.form.get("MessageStatus")  # queued/sent/delivered/failed/undelivered
        err = request.form.get("ErrorCode")  # e.g., 21610 unsubscribe, 30003 unknown, etc.
        
        app.logger.info(f"Status callback: {to_num} - {status} (Error: {err})")
        
        # React to compliance/blocked signals
        if err == "21610":
            # Recipient has opted out from Twilio side → mark locally
            upsert_subscriber(to_num, status="unsubscribed", last_keyword="STOP(21610)")
            app.logger.info(f"Marked {to_num} as unsubscribed due to error 21610")
        elif status in {"undelivered", "failed"} and err in {"21608", "30003"}:
            # 21608: Permission to send SMS not enabled for region
            # 30003: Unreachable/unknown handset
            app.logger.warning(f"Message to {to_num} failed: {status} (Error: {err})")
        
        return ("", 204)  # No content response
        
    except Exception as e:
        app.logger.error(f"Error in status callback: {str(e)}")
        return ("", 500)

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """Legacy endpoint - redirects to new inbound endpoint"""
    app.logger.warning("Legacy /sms endpoint called - redirecting to /sms/inbound")
    return sms_inbound()

@app.route("/health", methods=['GET'])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": __version__}, 200

@app.route("/webhook-urls", methods=['GET'])
def get_webhook_urls():
    """Get webhook URLs for Twilio configuration"""
    if twilio_utils:
        return twilio_utils.get_webhook_urls(), 200
    else:
        return {"error": "Twilio not configured"}, 500

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=25025)

