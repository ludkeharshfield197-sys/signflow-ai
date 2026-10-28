#!/bin/sh
set -eu

if [ "${RUN_DJANGO_BOOTSTRAP:-0}" = "1" ]; then
  python manage.py migrate --noinput
  python manage.py sync_model_cards
  python manage.py collectstatic --noinput
fi

exec "$@"
