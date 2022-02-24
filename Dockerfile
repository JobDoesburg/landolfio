FROM python:3.10 AS base

WORKDIR /usr/src/app

FROM base AS requirements-builder

RUN pip install poetry==1.1.8
COPY pyproject.toml .
COPY poetry.lock .
RUN poetry export -f requirements.txt -o requirements.txt

FROM base AS final

COPY --from=requirements-builder /usr/src/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD website website

WORKDIR /usr/src/app/website

RUN ./manage.py collectstatic --noinput --settings=website.settings.development

CMD [ "sh", "-c", "./manage.py migrate --settings=website.settings.production && gunicorn website.wsgi --bind=0.0.0.0:80 --env DJANGO_SETTINGS_MODULE=website.settings.production" ]
