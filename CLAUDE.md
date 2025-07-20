# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Setup

Landolfio is a Django-based business management system using Poetry for dependency management.

### Initial Setup
```bash
poetry install
poetry run pre-commit install
poetry shell
cd landolfio
export DJANGO_SETTINGS_MODULE=website.settings.development
python ./manage.py migrate
python ./manage.py runserver
```

### Common Commands

**Development server:**
```bash
cd landolfio
export DJANGO_SETTINGS_MODULE=website.settings.development
python ./manage.py runserver
```

**Database migrations:**
```bash
cd landolfio
python ./manage.py makemigrations
python ./manage.py migrate
```

**Testing:**
```bash
cd landolfio
python ./manage.py test --settings=website.settings.development
```

**Code quality:**
```bash
poetry run black .
poetry run pylint landolfio/
poetry run pre-commit run --all-files
```

**Load sample data:**
```bash
cd landolfio
python ./manage.py loaddata assets
```

## Development Workflow Preferences

### Code Style & Approach
- **Minimal output** - Keep responses concise, avoid unnecessary explanations
- **Direct solutions** - Address the specific request without elaboration
- **No comments** - Don't add code comments unless explicitly requested
- **Existing patterns** - Follow established code conventions and patterns
- **Security first** - Never expose secrets, follow Django security best practices
- **I typically run the server in reload mode in the background while using claude**

[... rest of the file remains unchanged ...]