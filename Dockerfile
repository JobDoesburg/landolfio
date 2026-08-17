FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# gcc + libpq-dev + python3-dev: needed to compile uWSGI from its sdist.
# curl + ca-certificates: needed by the compose healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev python3-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

# Copy only the lock/manifest first to leverage Docker cache
COPY pyproject.toml uv.lock /app/

# Install prod dependencies into a project-local .venv
RUN uv sync --locked --group prod --no-dev

# Put the venv on PATH so `python` / `uwsgi` resolve without `uv run`
ENV PATH="/app/.venv/bin:$PATH"

COPY landolfio /app
COPY entrypoint.sh /

ENV DJANGO_SETTINGS_MODULE=website.settings.production

ENV DJANGO_STATIC_ROOT=/static
ENV DJANGO_MEDIA_ROOT=/media
ENV DJANGO_STATIC_URL=/static/
ENV DJANGO_MEDIA_URL=/media/

RUN mkdir -p $DJANGO_STATIC_ROOT $DJANGO_MEDIA_ROOT \
    && touch /var/log/django.log /var/log/uwsgi.log \
    && python manage.py collectstatic --noinput \
    && chown -R nobody:nogroup $DJANGO_MEDIA_ROOT /var/log/django.log /var/log/uwsgi.log

EXPOSE 80

# entrypoint.sh runs migrations, then either execs uWSGI (no args) or the
# command passed via Compose `command:` (workers, scheduler, manage.py ...).
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
