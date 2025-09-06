#!/bin/bash

# AirPuff SMS Deployment Script with Virtual Environment
# This script ensures PyYAML is available for the deployment process

set -e

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source .venv/bin/activate
pip install pyyaml

# Run the deployment script
echo "Running deployment..."
./deploy.sh "$@"
