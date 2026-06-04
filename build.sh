#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# ── Compile Tailwind CSS ──────────────────────────────────────────────────────
# Download the Linux x64 Tailwind CLI binary (not committed — Windows .exe won't
# run on Render's Linux environment).
echo "Downloading Tailwind CSS CLI..."
curl -sLo tailwindcss https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss
echo "Compiling Tailwind CSS..."
./tailwindcss -i static/css/input.css -o static/css/output.css --minify
echo "Tailwind CSS compiled successfully."

# ── Django ────────────────────────────────────────────────────────────────────
python manage.py collectstatic --noinput
python manage.py migrate --noinput
