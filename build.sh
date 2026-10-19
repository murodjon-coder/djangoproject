#!/usr/bin/env bash
# Render.com build skripti: kutubxonalar, static fayllar, migratsiya va demo ma'lumotlar
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py seed_demo

# Admin akkaunti (Render "Environment" bo'limida DJANGO_SUPERUSER_USERNAME va DJANGO_SUPERUSER_PASSWORD berilsa)
if [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py createsuperuser --no-input || true
fi
