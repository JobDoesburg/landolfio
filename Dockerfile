FROM python:3.11-slim
ENV PYTHONUNBUFFERED 1
ENV PATH /root/.local/bin:${PATH}
ENV DJANGO_SETTINGS_MODULE website.settings.production

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
