#!/bin/bash

set -e  # Exit on any error

echo "🔧 Running pre-start scripts..."

# Example custom commands before runserver
python manage.py collectstatic --noinput
# python manage.py makemigrations
python manage.py migrate
echo "✅ Pre-commands done."

# Now run Django server
exec python manage.py runserver 0.0.0.0:8000
