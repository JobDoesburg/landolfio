FROM python:3.10
ENV PYTHONUNBUFFERED 1
ENV PATH /root/.poetry/bin:${PATH}
ENV DJANGO_SETTINGS_MODULE website.settings.production

ENTRYPOINT ["/landolfio/entrypoint.sh"]

WORKDIR /landolfio/src/
COPY entrypoint.sh /landolfio/entrypoint.sh
COPY poetry.lock pyproject.toml /landolfio/src/

RUN mkdir --parents /landolfio/src/
RUN mkdir --parents /landolfio/log/
RUN mkdir --parents /landolfio/static/
RUN mkdir --parents /landolfio/media/
RUN chmod +x /landolfio/entrypoint.sh

RUN curl -sSL https://install.python-poetry.org | python && \
        export PATH="/root/.local/bin:$PATH" && \
        poetry config --no-interaction --no-ansi virtualenvs.create false && \
        poetry install --no-interaction --no-ansi --no-dev --extras "production"

COPY landolfio /landolfio/src/

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install --yes --quiet --no-install-recommends iputils-ping && \
    rm --recursive --force /var/lib/apt/lists/*
