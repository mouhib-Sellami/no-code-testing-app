#!/bin/sh
python3 manage.py migrate

gunicorn --reload --bind 0.0.0.0:8000 no_code_testing_app_server.wsgi:application