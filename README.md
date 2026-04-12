# Landolfio

A Django-based asset and inventory management system with integrated Moneybird accounting synchronization.

![Build and push](https://github.com/GipHouse/Landolfio-2022/actions/workflows/build-and-push.yaml/badge.svg?branch=master)

## Features

- **Asset & Inventory Management** - Comprehensive asset tracking with properties, categories, locations, status changes, and attachments
- **Automated Moneybird Sync** - Nightly synchronization to automatically link assets with Moneybird accounting
- **Scan Tag System** - Generate and manage QR codes/barcodes for physical asset identification
- **New Customer Registration** - Streamlined forms for onboarding regular and rental customers with SEPA mandate handling
- **Ticketing System** - Track and manage various types of tickets
- **Contact Management** - Maintain customer and contact records synced with Moneybird
- **Multi-language Support** - Dutch language support with internationalization framework

## Tech Stack

- **Framework**: Django 6.0
- **Python**: 3.12+
- **Database**: PostgreSQL
- **Task Queue**: Django Tasks with database backend
- **Web Server**: Gunicorn/uWSGI with Nginx
- **Storage**: AWS S3 via django-storages
- **Containerization**: Docker with Docker Compose

## Development Setup

### Prerequisites

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- PostgreSQL (optional - SQLite used by default in development)

### Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd landolfio

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install

# Activate virtual environment
poetry shell

# Navigate to Django project
cd landolfio

# Set development settings
export DJANGO_SETTINGS_MODULE=website.settings.development

# Initialize database
python ./manage.py migrate

# (Optional) Load sample data
python ./manage.py loaddata assets

# Start development server
python ./manage.py runserver
```

The application will be available at `http://localhost:8000`

### Common Commands

**Run development server:**
```bash
cd landolfio
export DJANGO_SETTINGS_MODULE=website.settings.development
python ./manage.py runserver
```

**Create/apply database migrations:**
```bash
cd landolfio
python ./manage.py makemigrations
python ./manage.py migrate
```

**Run tests:**
```bash
cd landolfio
python ./manage.py test --settings=website.settings.development
```

**Code quality checks:**
```bash
poetry run black .
poetry run pylint landolfio/
poetry run pre-commit run --all-files
```

## Production Deployment

### Docker Compose

The project includes a complete Docker Compose setup with:

- **Web Service** - Django application with Gunicorn
- **Database** - PostgreSQL 14
- **Nginx** - Reverse proxy with automatic SSL via Let's Encrypt
- **Task Worker** - Background task processor
- **Task Scheduler** - Cron-based task scheduler

### Required Environment Variables

```bash
# Django
LANDOLFIO_SECRET_KEY=<secret-key>
LANDOLFIO_ALLOWED_HOSTS=<domain>
DJANGO_SETTINGS_MODULE=website.settings.production

# Database
POSTGRES_DB=<database-name>
POSTGRES_USER=<database-user>
POSTGRES_PASSWORD=<database-password>
POSTGRES_HOST=database
POSTGRES_PORT=5432

# Moneybird Integration
MONEYBIRD_ADMINISTRATION_ID=<admin-id>
MONEYBIRD_API_KEY=<api-key>
MONEYBIRD_MARGIN_ASSETS_LEDGER_ACCOUNT_ID=<account-id>
MONEYBIRD_NOT_MARGIN_ASSETS_LEDGER_ACCOUNT_ID=<account-id>

# AWS S3 Storage
AWS_ACCESS_KEY_ID=<access-key>
AWS_SECRET_ACCESS_KEY=<secret-key>
AWS_STORAGE_BUCKET_NAME=<bucket-name>
AWS_S3_REGION_NAME=<region>

# Email (SMTP)
SMTP_HOST=<smtp-host>
SMTP_PORT=<smtp-port>
SMTP_USE_TLS=true
SMTP_USER=<smtp-user>
SMTP_PASSWORD=<smtp-password>
SMTP_FROM=<from-address>
SMTP_FROM_EMAIL=<from-email>

# Monitoring
SENTRY_DSN=<sentry-dsn>
DJANGO_LOG_LEVEL=INFO
```

### Deploy with Docker Compose

```bash
# Pull latest image
docker-compose pull

# Start services
docker-compose up -d

# View logs
docker-compose logs -f web
```

## Architecture

### Background Tasks

Landolfio uses Django Tasks for asynchronous job processing with two separate services:

- **Task Scheduler** (`task-scheduler`) - Evaluates cron schedules and enqueues tasks
- **Task Worker** (`task-worker`) - Processes queued tasks from the database

#### Automated Tasks

**Nightly Asset Sync** (3 AM daily)
- Fetches all assets from Moneybird
- Automatically links unlinked assets based on name matching
- Logs sync statistics and unmatched assets

### Moneybird Integration

The system integrates with Moneybird accounting software for:
- Asset management and tracking
- Automated asset synchronization
- Financial data synchronization

## Project Structure

```
landolfio/
├── accounting/          # Contact and subscription management
├── inventory/          # Core asset and inventory management
├── tickets/            # Ticketing system
├── new_customers/      # New customer registration forms
├── new_rental_customers/ # Rental customer registration forms
├── scantags/           # QR code/barcode generation for asset tagging
├── moneybird/          # Moneybird API integration layer
├── ninox_import/       # Ninox database import utilities
├── website/            # Django project settings and configuration
├── inventory_frontend/ # Frontend UI components
└── locale/             # Internationalization/translation files
```

## Testing

Run the test suite:

```bash
cd landolfio
python ./manage.py test --settings=website.settings.development
```

Run with coverage:

```bash
poetry run coverage run --source='.' manage.py test --settings=website.settings.development
poetry run coverage report
```

## Contributing

1. Create a feature branch from `development`
2. Make your changes
3. Ensure all tests pass and code quality checks succeed
4. Submit a pull request to `development`

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting (target Python 3.12)
- Run pylint before committing
- Pre-commit hooks will enforce style automatically

## About

Landolfio is custom business management software created by Job Doesburg for VOF Doesburg. While the code is open source and available for use, it is highly specialized for specific business needs and comes with no warranty or support.

## License

MIT License - You are free to use, fork, and modify this software for your own purposes. See the LICENSE file for details.

**Note**: This software is provided "as is" without warranty of any kind. No support or maintenance is guaranteed.