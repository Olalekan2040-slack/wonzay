#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Compile Tailwind CSS
if [ -f "tailwindcss" ]; then
    ./tailwindcss -i static/css/input.css -o static/css/output.css --minify
fi

python manage.py collectstatic --noinput
python manage.py migrate --noinput
