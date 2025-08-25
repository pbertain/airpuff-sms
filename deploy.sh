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
    
    # Load environment variables
    env_vars = config.get('environment', {})
    for key, value in env_vars.items():
        if value != 'your_checkwx_api_key_here' and value != 'your_twilio_account_sid_here' and value != 'your_twilio_auth_token_here':
            print('export ' + key + '=\"' + str(value) + '\"')
        else:
            print('echo \"Warning: ' + key + ' still has default value\" >&2')
            sys.exit(1)
    
    # Load deployment configuration
    deployment = config.get('deployment', {})
    if deployment.get('app_dir'):
        print('export AIRPUFF_APP_DIR=\"' + str(deployment['app_dir']) + '\"')
    if deployment.get('log_dir'):
        print('export AIRPUFF_LOG_DIR=\"' + str(deployment['log_dir']) + '\"')
    if deployment.get('port'):
        print('export AIRPUFF_PORT=\"' + str(deployment['port']) + '\"')
        
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
    echo "  environment:"
    echo "    CHECKWX_API_KEY: 'your_actual_api_key'"
    echo "    TWILIO_ACCOUNT_SID: 'your_actual_sid'"
    echo "    TWILIO_AUTH_TOKEN: 'your_actual_token'"
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
