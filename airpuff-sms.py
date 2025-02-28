import os
import time
import logging
from flask import Flask, request, g
from lib import airpuff_lib
from twilio.twiml.messaging_response import MessagingResponse
from logging.handlers import RotatingFileHandler

# Script version
__version__ = "4"

# Twilio credentials (ensure to keep them safe and secure)
ACCOUNT_SID = 'ACa9dd12272b3de0539a2005c7e450b14c'
AUTH_TOKEN = 'f79b71e09ec390c05f0b180d5bda11b0'

SMS_REPLY_HAMPUFF = 'Wrong number. Text Hampuff at sms://+1-361-426-7833/ [361-HAM-PUFF]'

app = Flask(__name__)

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
        "request_data": request.values.get('Body', '').strip(),
        "user_agent": user_agent,
        "response_time": round(response_time, 4)
    }
    log_message = (
        f"{log_data['ip']} {log_data['status_code']} \"{log_data['request_data']}\" "
        f"{log_data['response_time']}s \"{log_data['user_agent']}\""
    )
    app.logger.info(log_message)
    return response

@app.route("/sms", methods=['GET', 'POST'])
def sms_reply():
    """
    Respond to incoming SMS with an appropriate reply.
    """
    try:
        full_body = request.values.get('Body', '')
        app.logger.info(f"Received Body: {full_body} (Type: {type(full_body)})")  # Log the type of input

        full_body = str(full_body).strip()  # Ensure full_body is a string

        if 'fuck' in body:
            sms_resp_body = "Go fuck yourself, too"
        elif 'shit' in body:
            sms_resp_body = "Go shit your pants"
        elif 'hampuff' in body:
            sms_resp_body = SMS_REPLY_HAMPUFF
        else:
            # Process as list of airport codes if valid
            codes = body.split()[:5]  # Limit to 5 codes max
            responses = []
            for code in codes:
                if len(code) <= 4:
                    responses.append(airpuff_lib.get_wx(code))
                else:
                    responses.append(f"{code.upper()}: Not a valid airport code.")
            sms_resp_body = "AirPuff:\n" + "\n".join(responses) + f"\n\n{airpuff_lib.CONSENT_MESSAGE}"

    except Exception as e:
        app.logger.error(f"Error processing message: {str(e)}")
        sms_resp_body = "Sorry, something went wrong while processing your request."

    # Start our TwiML response
    resp = MessagingResponse()
    resp.message(sms_resp_body)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True, host='127.0.0.1', port=5000)

