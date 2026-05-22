# System Settings Usage

This document explains how to use the system settings functionality in your application.

## Overview

System settings are stored in the database and can be accessed throughout the application using the `Settings` utility class.

## Admin Interface

Administrators can manage system settings through the admin panel:
- Navigate to `/admin/system-settings`
- Update any settings and click "Save Changes"
- Settings are immediately persisted to the database

## Using Settings in Code

### Import the Settings Class

```python
from app.utils.settings import Settings
```

### Get a Single Setting

```python
# Get a string value
site_name = Settings.get('site_name')
support_email = Settings.get('support_email', default='support@example.com')

# Get a boolean value
is_maintenance = Settings.get_bool('maintenance_mode')
enable_cod = Settings.get_bool('enable_cod')

# Get an integer value
session_lifetime = Settings.get_int('session_lifetime')
max_attempts = Settings.get_int('max_login_attempts')
```

### Get All Settings

```python
all_settings = Settings.get_all()
# Returns: {'site_name': 'PawfectFinds', 'admin_email': 'admin@...', ...}
```

### Update a Setting Programmatically

```python
# Update a single setting
Settings.set('site_name', 'My New Site Name')

# Update multiple settings at once
Settings.set_multiple({
    'site_name': 'New Name',
    'maintenance_mode': '1',
    'max_login_attempts': '10'
})
```

## Available Settings

### General
- `site_name` - Website name
- `site_description` - Website description
- `admin_email` - Administrator email
- `support_email` - Support email
- `default_currency` - Default currency (USD, EUR, PHP)
- `timezone` - System timezone

### Security
- `maintenance_mode` - Enable/disable maintenance mode (0/1)
- `require_email_verification` - Require email verification (0/1)
- `session_lifetime` - Session lifetime in minutes
- `max_login_attempts` - Maximum login attempts

### Business Rules
- `max_products_per_seller` - Maximum products per seller
- `order_auto_cancel_days` - Days before auto-canceling orders
- `featured_products_limit` - Number of featured products

### Payment
- `enable_cod` - Enable cash on delivery (0/1)
- `enable_card` - Enable card payments (0/1)
- `payment_provider` - Payment provider (stripe, paypal, paymongo, none)
- `payment_public_key` - Payment provider public key

### Email
- `smtp_host` - SMTP server host
- `smtp_port` - SMTP server port
- `smtp_tls` - Use TLS for SMTP (0/1)
- `email_from` - Email from address
- `email_theme` - Email template theme

## Example Use Cases

### Checking Maintenance Mode

```python
from app.utils.settings import Settings
from flask import abort

@app.before_request
def check_maintenance():
    if Settings.get_bool('maintenance_mode'):
        if not is_admin():
            abort(503)  # Service Unavailable
```

### Using Currency Settings

```python
currency = Settings.get('default_currency', 'USD')
currency_symbol = {
    'USD': '$',
    'EUR': '€',
    'PHP': '₱'
}.get(currency, '$')
```

### Enforcing Product Limits

```python
max_products = Settings.get_int('max_products_per_seller', 100)
current_products = Product.count_by_seller(seller_id)

if current_products >= max_products:
    flash(f'You have reached the maximum limit of {max_products} products.', 'error')
    return redirect(url_for('seller.products'))
```

### Email Configuration

```python
smtp_config = {
    'host': Settings.get('smtp_host'),
    'port': Settings.get_int('smtp_port', 587),
    'use_tls': Settings.get_bool('smtp_tls', True),
    'from_address': Settings.get('email_from', 'noreply@example.com')
}
```

## Testing

You can test settings from the command line:

```bash
# Get all settings
python -c "from app.utils.settings import Settings; import json; print(json.dumps(Settings.get_all(), indent=2))"

# Get a specific setting
python -c "from app.utils.settings import Settings; print(Settings.get('site_name'))"

# Update a setting
python -c "from app.utils.settings import Settings; Settings.set('maintenance_mode', '1'); print('Maintenance mode enabled')"
```

## Database Schema

Settings are stored in the `system_settings` table:

```sql
CREATE TABLE system_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type VARCHAR(50) DEFAULT 'string',
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```
