#!/bin/bash

set -e

FIXTURE_FILE=./exported_data.json
DEPLOY=false
UPDATE=false

# Parse arguments
for arg in "$@"; do
    if [[ "$arg" == "deploy" ]]; then
        DEPLOY=true
    fi
    if [[ "$arg" == "update" ]]; then
        UPDATE=true
    fi
done

echo "Fixture file to load: $FIXTURE_FILE"

echo "🔧 Checking for MariaDB dependencies..."

# Check if pkg-config is installed
if ! dpkg -s pkg-config &>/dev/null; then
    echo "📦 Installing pkg-config..."
    sudo apt-get update
    sudo apt-get install -y pkg-config
else
    echo "✅ pkg-config already installed."
fi

# Check if libmariadb-dev is installed
if ! dpkg -s libmariadb-dev &>/dev/null; then
    echo "📦 Installing libmariadb-dev..."
    sudo apt-get update
    sudo apt-get install -y libmariadb-dev
else
    echo "✅ libmariadb-dev already installed."
fi

# Check if MariaDB is already running
if ! systemctl is-active --quiet mariadb; then
    echo "🔧 Installing MariaDB server..."
    sudo apt install -y mariadb-server
    echo "🔧 Starting MariaDB server..."
    sudo systemctl start mariadb
else
    echo "✅ MariaDB server is already running."
fi

# Check root access to MariaDB
echo "🔍 Checking root access..."
if mysql -u root -e "SELECT 1" &>/dev/null; then
    echo "⚠️  No root password detected. Setting a new password..."
    sudo mariadb -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASS';
FLUSH PRIVILEGES;
EOF
    if [ $? -ne 0 ]; then
        echo "❌ Failed to set root password."
        exit 1
    fi
    echo "✅ Root password successfully set."
else
    echo "✅ Root password is already set. Proceeding..."
fi

if ! mysql -u root -p"$DB_ROOT_PASS" -e "SELECT 1" &>/dev/null; then
    echo "❌ Incorrect root password. Check the DB_ROOT_PASS variable."
    exit 1
fi

# If "update" is specified or mousetube_api is not installed, install/reinstall
if [ "$UPDATE" == true ] || ! python3 -c "import mousetube_api" &>/dev/null; then
    echo "📦 mousetube_api not found or 'update' flag specified. Installing/reinstalling dependencies..."
    pip install --upgrade pip
    pip install -e .
else
    echo "✅ mousetube_api is already installed, skipping installation."
fi

# If the environment file exists, load it
if [ -f mousetube.env ]; then
    export $(grep -v '^#' mousetube.env | xargs)
elif [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env or mousetube.env file found!"
    exit 1
fi

echo "🔍 Checking if database '$DB_NAME' already exists and contains tables..."

DB_TABLE_COUNT=$(mysql -u root -p"$DB_ROOT_PASS" -N -B -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '$DB_NAME';")

if [ "$DB_TABLE_COUNT" -gt 0 ]; then
    echo "✅ Database '$DB_NAME' already exists and contains tables. Skipping recreation."
else
    echo "⚠️  This operation will delete and recreate the database '$DB_NAME'. Continue? (y/n)"
    read CONFIRM
    if [ "$CONFIRM" != "y" ]; then
        echo "❌ Operation canceled."
        exit 1
    fi

    echo "🚀 Recreating the database..."
    sudo mariadb -u root -p"$DB_ROOT_PASS" <<EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

    if [ $? -ne 0 ]; then
        echo "❌ Error configuring the database."
        exit 1
    fi
fi

echo "🐍 Running Django migrations..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

# Optional: load fixtures
if [ -f "$FIXTURE_FILE" ]; then
    echo "📦 Loading Django fixture from $FIXTURE_FILE..."
    python3 manage.py loaddata "$FIXTURE_FILE"
fi

# Collect static files in production mode
if [ "$DEBUG" == "false" ]; then
    echo "📦 Collecting static files..."
    python3 manage.py collectstatic --noinput
fi

# Start the server if in "deploy" mode
if [ "$DEPLOY" == "true" ]; then
    if [ "$DEBUG" == "false" ]; then
        echo "🚀 Starting Gunicorn server..."
        exec gunicorn madbot_api.asgi:application --bind 0.0.0.0:8000 --timeout 420 -k uvicorn.workers.UvicornWorker
    else
        echo "⚙️ Starting development server..."
        exec python3 manage.py runserver 0.0.0.0:8000
    fi
else
    echo "✅ Setup complete. Server not started (no 'deploy' flag)."
fi