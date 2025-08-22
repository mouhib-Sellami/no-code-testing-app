#!/bin/sh

python3 manage.py makemigrations --skip-check
python3 manage.py migrate_schemas --shared --skip-check
python3 manage.py collectstatic --noinput --skip-check
# python3 manage.py load_providers_config --skip-check
python3 manage.py create_public_tenant --domain_url $APP_URL --owner_email admin@domain.com --skip-check
python manage.py custom_create_tenant_superuser --schema public --skip-checks

export HF_API_TOKEN=$HUGGING_FACES_API_KEY

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