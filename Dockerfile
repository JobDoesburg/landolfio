FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# gcc + libpq-dev + python3-dev: needed to compile uWSGI from its sdist.
# curl + ca-certificates: needed by the compose healthcheck.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev python3-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY pyproject.toml poetry.lock /app/

# Install project dependencies
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --with prod --no-interaction --no-ansi --no-root

# Copy the current directory contents into the container at /app
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

# Command to run uWSGI
CMD ["/bin/sh", "/entrypoint.sh"]