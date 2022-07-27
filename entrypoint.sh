#!/bin/sh
set -e

echo "Running site"

chown -R www-data:www-data /landolfio/

cd /landolfio/src

touch -a /landolfio/log/uwsgi.log
touch -a /landolfio/log/django.log

python manage.py collectstatic --no-input
python manage.py migrate --no-input

uwsgi --chdir=/landolfio/src/ \
    --module=website.wsgi:application \
    --master --pidfile=/tmp/project-master.pid \
    --socket=:8000 \
    --processes=5 \
    --uid=www-data --gid=www-data \
    --harakiri=600 \
    --post-buffering=16384 \
    --max-requests=5000 \
    --thunder-lock \
    --vacuum \
    --logfile-chown \
    --logto2=/landolfio/log/uwsgi.log \
    --ignore-sigpipe \
    --ignore-write-errors \
    --disable-write-exception \
    --enable-threads
