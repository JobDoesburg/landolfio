FROM python:3.10
ENV PYTHONUNBUFFERED 1
ENV PATH /root/.local/bin:${PATH}
ENV DJANGO_SETTINGS_MODULE website.settings.production

WORKDIR /landolfio/src/
COPY poetry.lock pyproject.toml /landolfio/src/

RUN curl -sSL https://install.python-poetry.org | python && \
        poetry config --no-interaction --no-ansi virtualenvs.create false && \
        poetry install --no-interaction --no-ansi --no-dev --extras "production"

RUN mkdir --parents /landolfio/src/
RUN mkdir --parents /landolfio/log/
RUN mkdir --parents /landolfio/static/
RUN mkdir --parents /landolfio/media/

COPY entrypoint.sh /landolfio/entrypoint.sh
RUN chmod +x /landolfio/entrypoint.sh

COPY landolfio /landolfio/src/

ENTRYPOINT ["/landolfio/entrypoint.sh"]
