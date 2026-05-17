#!/bin/sh
# Common boot for every Django container: web, task-worker, task-scheduler.
# Apply migrations first so workers don't race the schema. Then dispatch:
#   - no argv  → web (uWSGI)
#   - any argv → exec it (worker / scheduler / one-off command)
set -e

python manage.py migrate --noinput

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

# Ensure the uWSGI logfile exists so tail -F doesn't print a spurious warning.
touch /var/log/uwsgi.log

# Stream uWSGI logs to stdout for `docker logs`.
tail -F /var/log/uwsgi.log &

exec uwsgi --http :80 \
      --wsgi-file /app/website/wsgi.py \
      --master \
      --processes 4 \
      --threads 2 \
      --enable-threads \
      --py-call-uwsgi-fork-hooks \
      --uid nobody \
      --gid nogroup \
      --static-map ${DJANGO_STATIC_URL}=${DJANGO_STATIC_ROOT} \
      --static-map ${DJANGO_MEDIA_URL}=${DJANGO_MEDIA_ROOT} \
      --logto /var/log/uwsgi.log \
      --log-date \
      --log-4xx \
      --log-5xx