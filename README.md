# AirPuff SMS Service

A Twilio-powered SMS service for providing weather information via text message.

## Features

- **Weather Information**: Get METAR/TAF data for airport codes
- **Subscriber Management**: Opt-in/opt-out compliance with Twilio Advanced Opt-Out
- **Security**: Twilio signature validation for webhook security
- **Delivery Tracking**: Status callbacks for message delivery monitoring
- **Compliance**: Automatic handling of STOP/START keywords

## Twilio Setup

### 1. Configure Your Twilio Phone Number

In your Twilio Console, set up your phone number with these webhooks:

- **Messaging webhook**: `POST https://your-domain.com/sms/inbound`
- **Status callback**: `POST https://your-domain.com/sms/status`

### 2. Enable Advanced Opt-Out

In Twilio Console > Messaging > Compliance:
- Enable "Advanced Opt-Out" for automatic compliance handling
- Twilio will automatically respond to STOP/START keywords

### 3. Environment Variables

Create a `config.yml` file with your Twilio credentials:

```yaml
# Twilio Configuration
twilio_account_sid: "your_twilio_account_sid_here"
twilio_auth_token: "your_twilio_auth_token_here"
twilio_from_number: "+1234567890"  # Your Twilio phone number

# Webhook URLs (must be publicly accessible HTTPS)
public_webhook_url: "https://your-domain.com"
public_status_url: "https://your-domain.com"

# API Keys
checkwx_api_key: "your_checkwx_api_key_here"
```

## API Endpoints

### SMS Webhook (`/sms/inbound`)
- **Method**: POST
- **Purpose**: Receives incoming SMS messages
- **Security**: Validates Twilio signature
- **Features**: 
  - Handles compliance keywords (STOP/START/HELP)
  - Processes weather requests for subscribed users
  - Manages subscriber status

### Status Callback (`/sms/status`)
- **Method**: POST
- **Purpose**: Receives delivery status updates
- **Security**: Validates Twilio signature
- **Features**: 
  - Tracks message delivery status
  - Handles compliance errors (e.g., 21610 for opt-outs)
  - Logs delivery failures

### Health Check (`/health`)
- **Method**: GET
- **Purpose**: Service health monitoring
- **Response**: Service status and version

### Webhook URLs (`/webhook-urls`)
- **Method**: GET
- **Purpose**: Get configured webhook URLs for Twilio setup

## Subscriber Management

The service automatically manages subscribers based on SMS interactions:

- **JOIN/START/YES**: Opts user in (consent logged)
- **STOP/STOPALL/UNSUBSCRIBE**: Opts user out
- **HELP/INFO**: Provides usage information
- **Weather requests**: Only processed for subscribed users

## Database Schema

Subscribers are stored in SQLite with this structure:

```sql
CREATE TABLE subscribers (
  phone_e164 TEXT PRIMARY KEY,
  status TEXT NOT NULL,              -- 'subscribed' | 'unsubscribed' | 'pending'
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  consent_ts TEXT,                   -- when they opted-in
  last_keyword TEXT                  -- last keyword we saw
);
```

## Deployment

### Prerequisites
- Python 3.6+
- Ansible for deployment
- Publicly accessible HTTPS domain

### Deploy with Ansible
```bash
./deploy.sh
```

The deployment script will:
1. Install dependencies
2. Set up the service
3. Configure systemd service
4. Create necessary directories and permissions

## Security Features

- **Twilio Signature Validation**: Prevents webhook spoofing
- **Environment Variable Configuration**: Secure credential management
- **Proper File Permissions**: Restricted access to sensitive files
- **Logging**: Comprehensive request and error logging

## Best Practices Implemented

- **Let Twilio handle compliance**: Advanced Opt-Out enabled
- **Signature validation**: Kept on for security
- **Consent logging**: Timestamps for opt-ins
- **Idempotency**: Safe handling of repeated keywords
- **Error handling**: Graceful degradation on failures
- **Status callbacks**: Proper delivery tracking

## Monitoring

- **Logs**: Rotating log files in `/var/log/airpuff-sms/`
- **Health checks**: `/health` endpoint for monitoring
- **Delivery tracking**: Status callbacks for message delivery
- **Subscriber metrics**: Database tracking of user engagement

## Troubleshooting

### Common Issues

1. **Webhook not receiving messages**: Check Twilio webhook URL configuration
2. **Signature validation errors**: Verify `PUBLIC_WEBHOOK_URL` environment variable
3. **Database errors**: Ensure proper permissions on `/opt/airpuff-sms/` directory
4. **Service not starting**: Check systemd logs with `journalctl -u airpuff-sms`

### Logs
- Application logs: `/var/log/airpuff-sms/access.log`
- System logs: `journalctl -u airpuff-sms`

## Development

### Local Testing
```bash
cd app
python airpuff-sms.py
```

### Adding Features
- New endpoints: Add routes to `airpuff-sms.py`
- Database changes: Update `lib/db_utils.py`
- Twilio integration: Extend `lib/twilio_utils.py`
- Outbound messaging: Use `lib/outbound_sms.py`
