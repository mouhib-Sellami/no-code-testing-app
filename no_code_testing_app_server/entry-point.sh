#!/bin/sh
gunicorn no_code_testing_app_server.wsgi -w 2 -b 0.0.0.0:8000 --reload
