#!/bin/sh
python manage.py migrate --noinput

# Start tail for uWSGI logs in background (send to stdout for docker logs)
tail -F /var/log/uwsgi.log &

# Start uWSGI (logs go to both file and stdout)
uwsgi --http :80 \
      --wsgi-file /app/website/wsgi.py \
      --master \
      --processes 4 \
      --threads 2 \
      --uid nobody \
      --gid nogroup \
      --static-map ${DJANGO_STATIC_URL}=${DJANGO_STATIC_ROOT} \
      --static-map ${DJANGO_MEDIA_URL}=${DJANGO_MEDIA_ROOT} \
      --logto /var/log/uwsgi.log \
      --log-date \
      --log-4xx \
      --log-5xx