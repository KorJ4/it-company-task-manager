#!/usr/bin/env bash
# Render build script: install packages, collect static, migrate, add demo data.
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py load_demo_data
