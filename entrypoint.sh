#!/bin/sh

echo "⏳ Waiting for MariaDB to be ready..."
# Try to connect with or without a password if it's the first time
until mariadb -h db -u root -p"$DB_ROOT_PASS" -e "SELECT 1" &>/dev/null || mariadb -h db -u root -e "SELECT 1" &>/dev/null; do
    echo "⏳ MariaDB is not ready yet, retrying in 5 seconds..."
    sleep 5
done
echo "✅ MariaDB is ready!"

echo "🔍 Checking root access..."

# If connection with password fails, try without password
if mariadb -h db -u root -p"$DB_ROOT_PASS" -e "SELECT 1" &>/dev/null; then
    echo "✅ Root password is already set. Proceeding..."
else
    echo "⚠️ No root password detected. Setting a new password..."
    
    if [ -z "$DB_ROOT_PASS" ]; then
        echo "❌ DB_ROOT_PASS is not set."
        exit 1
    fi

    # If root password is not set, configure it
    mariadb -h db -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASS';
FLUSH PRIVILEGES;
EOF
    if [ $? -ne 0 ]; then
        echo "❌ Failed to set root password."
        exit 1
    fi
    echo "✅ Root password successfully set."
fi

# Check if DB_NAME and DB_USER are set
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ]; then
    echo "❌ DB_NAME or DB_USER is not set."
    exit 1
fi

echo "🚀 Recreating the database..."
mariadb -h db -u root -p"$DB_ROOT_PASS" <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

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