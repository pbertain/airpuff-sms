#!/bin/bash

# AirPuff SMS Deployment Script
# Usage: ./deploy.sh [inventory_file] [host]

set -e

# Default values
INVENTORY_FILE="ansible/inventory.yml"
HOST=""
CONFIG_FILE="config.yml"

# Parse command line arguments
if [ $# -ge 1 ]; then
    INVENTORY_FILE="$1"
fi

if [ $# -ge 2 ]; then
    HOST="$2"
fi

# Check if inventory file exists
if [ ! -f "$INVENTORY_FILE" ]; then
    echo "Error: Inventory file '$INVENTORY_FILE' not found!"
    echo "Please create an inventory file or specify a different one."
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file '$CONFIG_FILE' not found!"
    echo "Please create a config.yml file with your environment variables."
    echo "See config.yml.example for a template."
    exit 1
fi

# Load environment variables from config.yml
echo "📋 Loading configuration from $CONFIG_FILE..."

# Use Python to parse YAML and export variables (more reliable than shell parsing)
eval "$(python3 -c "
import yaml
import sys

try:
    with open('$CONFIG_FILE', 'r') as f:
        config = yaml.safe_load(f)
    
    # Load Twilio configuration
    if 'twilio_account_sid' in config:
        print('export TWILIO_ACCOUNT_SID=\"' + str(config['twilio_account_sid']) + '\"')
    if 'twilio_auth_token' in config:
        print('export TWILIO_AUTH_TOKEN=\"' + str(config['twilio_auth_token']) + '\"')
    if 'twilio_from_number' in config:
        print('export TWILIO_FROM_NUMBER=\"' + str(config['twilio_from_number']) + '\"')
    
    # Load webhook URLs
    if 'public_webhook_url' in config:
        print('export PUBLIC_WEBHOOK_URL=\"' + str(config['public_webhook_url']) + '\"')
    if 'public_status_url' in config:
        print('export PUBLIC_STATUS_URL=\"' + str(config['public_status_url']) + '\"')
    
    # Load API keys
    if 'checkwx_api_key' in config:
        print('export CHECKWX_API_KEY=\"' + str(config['checkwx_api_key']) + '\"')
    
    # Load service configuration
    if 'airpuff_app_dir' in config:
        print('export AIRPUFF_APP_DIR=\"' + str(config['airpuff_app_dir']) + '\"')
    if 'airpuff_log_dir' in config:
        print('export AIRPUFF_LOG_DIR=\"' + str(config['airpuff_log_dir']) + '\"')
    if 'airpuff_port' in config:
        print('export AIRPUFF_PORT=\"' + str(config['airpuff_port']) + '\"')
        
except Exception as e:
    print('echo \"Error parsing config file: ' + str(e) + '\" >&2', file=sys.stderr)
    sys.exit(1)
")"

# Check if required environment variables are set
if [ -z "$CHECKWX_API_KEY" ] || [ -z "$TWILIO_ACCOUNT_SID" ] || [ -z "$TWILIO_AUTH_TOKEN" ]; then
    echo "Error: Required environment variables are not set!"
    echo "Please update your $CONFIG_FILE file with the actual values."
    echo ""
    echo "Example:"
    echo "  twilio_account_sid: 'your_actual_sid'"
    echo "  twilio_auth_token: 'your_actual_token'"
    echo "  checkwx_api_key: 'your_actual_api_key'"
    exit 1
fi

echo "🚀 Deploying AirPuff SMS Service..."
echo "📁 Inventory: $INVENTORY_FILE"
echo "📋 Config: $CONFIG_FILE"
if [ -n "$HOST" ]; then
    echo "🎯 Target host: $HOST"
fi
echo "🔑 API Key: ${CHECKWX_API_KEY:0:8}..."
echo "📱 Twilio SID: ${TWILIO_ACCOUNT_SID:0:8}..."

# Show deployment configuration if set
if [ -n "$AIRPUFF_APP_DIR" ]; then
    echo "📂 App Directory: $AIRPUFF_APP_DIR"
fi
if [ -n "$AIRPUFF_LOG_DIR" ]; then
    echo "📋 Log Directory: $AIRPUFF_LOG_DIR"
fi
if [ -n "$AIRPUFF_PORT" ]; then
    echo "🌐 Port: $AIRPUFF_PORT"
fi
if [ -n "$PUBLIC_WEBHOOK_URL" ]; then
    echo "🌐 Webhook URL: $PUBLIC_WEBHOOK_URL"
fi
if [ -n "$PUBLIC_STATUS_URL" ]; then
    echo "📊 Status URL: $PUBLIC_STATUS_URL"
fi
echo ""

# Run the Ansible playbook
if [ -n "$HOST" ]; then
    ansible-playbook -i "$INVENTORY_FILE" ansible/deploy.yml --limit "$HOST"
else
    ansible-playbook -i "$INVENTORY_FILE" ansible/deploy.yml
fi

echo ""
echo "✅ Deployment completed successfully!"
echo "🔍 Check the service status with: sudo systemctl status airpuff-sms"
echo "📋 View logs with: sudo journalctl -u airpuff-sms -f"
