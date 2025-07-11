#!/bin/sh
python3 manage.py makemigrations
python3 manage.py migrate

gunicorn \
  --reload \
  --workers 4 \
  --timeout 30 \
  --keep-alive 5 \
  --worker-class gthread \
  --threads 4 \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --bind 0.0.0.0:8000 \
  no_code_testing_app_server.wsgi:application