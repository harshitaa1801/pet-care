#!/bin/sh
set -e

cd /app

# Check if the database is ready and wait for it
echo "Waiting for DB to be ready..."
until python manage.py check
do
    echo "Waiting for DB..."
    sleep 2
done

./manage.py makemigrations

# Apply database migrations (only if there are changes)
echo "Applying migrations..."
./manage.py migrate 

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn..."
# gunicorn pet-care.wsgi:application --bind 0.0.0.0:8000 --workers 2 --threads 2

echo "Executing command: $@"
exec "$@"