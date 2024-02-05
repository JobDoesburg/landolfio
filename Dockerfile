FROM python:3.11-slim
ENV PATH /root/.local/bin:${PATH}
ENV DJANGO_SETTINGS_MODULE website.settings.production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev python3-dev cron libxmlsec1-dev libxmlsec1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /landolfio/src/
COPY poetry.lock pyproject.toml /landolfio/src/

RUN pip install poetry \
    && poetry config virtualenvs.create false  \
    && poetry install --no-interaction --no-ansi --no-dev --extras "production"

RUN mkdir --parents /landolfio/src/
RUN mkdir --parents /landolfio/log/
RUN mkdir --parents /landolfio/static/
RUN mkdir --parents /landolfio/media/

COPY entrypoint.sh /landolfio/entrypoint.sh
RUN chmod +x /landolfio/entrypoint.sh

COPY landolfio /landolfio/src/

ENTRYPOINT ["/landolfio/entrypoint.sh"]
