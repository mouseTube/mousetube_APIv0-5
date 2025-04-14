#!/bin/sh

echo "🛠️ Running makemigrations..."
python3 manage.py makemigrations --noinput

echo "📦 Applying migrations..."
python3 manage.py migrate --noinput

if [ -n "$FIXTURE_FILE" ] && [ -f "$FIXTURE_FILE" ]; then
    echo "📥 Loading fixture from $FIXTURE_FILE..."
    python3 manage.py loaddata "$FIXTURE_FILE"
else
    echo "⚠️ Fixture file not found or not defined. Skipping fixture loading."
fi

if [ "$DEBUG" = "false" ]; then
    echo "🧪 Collecting static files..."
    python3 manage.py collectstatic --noinput

    echo "🚀 Starting Gunicorn server..."
    exec gunicorn madbot_api.asgi:application --bind 0.0.0.0:8000 --timeout 420 -k uvicorn.workers.UvicornWorker
else
    echo "⚙️ Starting development server..."
    exec python3 manage.py runserver 0.0.0.0:8000
fi