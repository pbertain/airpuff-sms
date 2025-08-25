# AirPuff SMS Service

A Flask-based SMS service that provides weather information for airports via Twilio.

## Repository Structure

```
airpuff-sms/
├── app/                    # Application code
│   ├── airpuff-sms.py     # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── lib/               # Library modules
├── ansible/               # Deployment configuration
│   ├── deploy.yml         # Main playbook
│   ├── inventory.yml      # Host inventory
│   ├── vars/              # Variables
│   ├── tasks/             # Task definitions
│   ├── handlers/          # Event handlers
│   ├── templates/         # Jinja2 templates
│   └── files/             # Static files
├── config.yml.example     # Configuration template
├── README.md              # This file
└── deploy.sh              # Deployment script
```

## Features

- SMS-based weather queries for airport codes
- Integration with CheckWX API for METAR data
- Twilio SMS integration
- Comprehensive logging and monitoring
- Ansible deployment automation

## Quick Start

### Local Development

1. Navigate to the app directory:
   ```bash
   cd app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export TWILIO_ACCOUNT_SID="your_account_sid"
   export TWILIO_AUTH_TOKEN="your_auth_token"
   export CHECKWX_API_KEY="your_checkwx_api_key"
   ```

4. Run the service:
   ```bash
   python airpuff-sms.py
   ```

The service will run on `http://127.0.0.1:25025`

## Deployment with Ansible

This repository includes Ansible playbooks for automated deployment.

### Prerequisites

- Target server running Ubuntu/Debian
- Ansible installed on your control machine
- SSH access to target server

### Configuration

1. **Set up your configuration file:**
   ```bash
   cp config.yml.example config.yml
   # Edit config.yml with your actual values
   ```

2. **Update the inventory file** with your SSH credentials in `ansible/inventory.yml`

3. **Test connectivity** to make sure Ansible can reach your hosts:
   ```bash
   ansible all -i ansible/inventory.yml -m ping
   ```

### Deployment

**Using the deployment script (recommended):**
```bash
./deploy.sh
```

**Using Ansible directly:**
```bash
ansible-playbook -i ansible/inventory.yml ansible/deploy.yml
```

**Deploy to specific hosts:**
```bash
./deploy.sh ansible/inventory.yml host77.nird.club
```

### What Gets Deployed

- Python application files from `app/` directory
- Systemd service for automatic startup
- Log rotation configuration
- Virtual environment with dependencies
- Proper file permissions and ownership

## Configuration

The deployment script automatically loads environment variables from `config.yml`. This file contains:

```yaml
environment:
  CHECKWX_API_KEY: "your_actual_checkwx_api_key"
  TWILIO_ACCOUNT_SID: "your_actual_twilio_account_sid"
  TWILIO_AUTH_TOKEN: "your_actual_twilio_auth_token"
```

**Security Note:** The `config.yml` file is automatically added to `.gitignore` to prevent accidentally committing sensitive credentials. Always use `config.yml.example` as a template.

## API Endpoints

- `POST /sms` - Main SMS endpoint for Twilio webhook

## SMS Usage

Send airport codes to the service:
- Single code: `KIAH`
- Multiple codes: `KIAH KHOU KDFW`

## Environment Variables

- `TWILIO_ACCOUNT_SID` - Your Twilio account SID
- `TWILIO_AUTH_TOKEN` - Your Twilio auth token
- `CHECKWX_API_KEY` - Your CheckWX API key for weather data

## Logging

Logs are written to `/var/log/airpuff-sms/access.log` with automatic rotation.

## Service Management

```bash
# Start the service
sudo systemctl start airpuff-sms

# Enable auto-start
sudo systemctl enable airpuff-sms

# Check status
sudo systemctl status airpuff-sms

# View logs
sudo journalctl -u airpuff-sms -f
```

## Development Workflow

1. **Application Changes**: Make changes in the `app/` directory
2. **Deployment Changes**: Modify Ansible files in the `ansible/` directory
3. **Configuration**: Update `config.yml` with your credentials
4. **Testing**: Test locally in the `app/` directory
5. **Deployment**: Use the deployment script to deploy to servers

## Version History

- Version 6: Improved error handling and logging
- Version 5: Fixed data parsing issues
- Version 4: Added comprehensive logging
- Version 3: Initial Twilio integration
- Version 2: Weather API integration
- Version 1: Basic Flask setup
