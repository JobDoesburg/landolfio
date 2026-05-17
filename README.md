# Landolfio

A Django-based asset and inventory management system with integrated Moneybird accounting synchronization.

![Build and push](https://github.com/JobDoesburg/landolfio/actions/workflows/build-and-push.yaml/badge.svg?branch=master)
![Deploy](https://github.com/JobDoesburg/landolfio/actions/workflows/deploy.yaml/badge.svg?branch=master)

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
- **Database**: PostgreSQL 17
- **Task Queue**: Django Tasks with database backend
- **Web Server**: uWSGI behind Caddy (auto-HTTPS)
- **Storage**: AWS S3 via django-storages
- **Containerization**: Docker Compose
- **Deployment**: Self-hosted GitHub Actions runner — every push to `master` builds an image and auto-deploys to production

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

Production runs on `landolfio.vofdoesburg.nl` as a Docker Compose stack
managed by a self-hosted GitHub Actions runner installed on the VM. Every
push to `master` triggers `Build and push` (publishes the image to GHCR),
which in turn triggers `Deploy` (writes the compose stack + `.env` from
GitHub Environment secrets and rolls the containers).

See [`deploy/README.md`](deploy/README.md) for the full runbook: VM
prerequisites, runner installation, GitHub Environment secrets and
variables, image tagging strategy, and rollback procedure.

The stack consists of:

- **caddy** — reverse proxy with automatic HTTPS
- **database** — PostgreSQL 17
- **web** — Django app served by uWSGI
- **task-worker** — background task processor
- **task-scheduler** — cron-based task scheduler

To cut a release, draft a GitHub Release with a `vX.Y.Z` tag — CI then
publishes a semver-tagged image alongside the immutable `sha-<sha>` tag.

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

1. Create a feature branch from `master`
2. Make your changes
3. Ensure all tests pass and code quality checks succeed
4. Submit a pull request to `master`

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