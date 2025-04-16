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

# Check if python3-dev is installed
if ! dpkg -s python3-dev &>/dev/null; then
    echo "📦 Installing python3-dev..."
    sudo apt-get update
    sudo apt-get install -y python3-dev
else
    echo "✅ python3-dev already installed."
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

# Wait until MariaDB is ready
echo "⏳ Waiting for MariaDB to be ready..."
until sudo mariadb -u root -e "SELECT 1" &>/dev/null; do
    echo "⏳ MariaDB is not ready yet, retrying in 5 seconds..."
    sleep 5
done
echo "✅ MariaDB is ready!"

# Check and configure root password
echo "🔍 Checking root access..."
if mariadb -u root -p"$DB_ROOT_PASS" -e "SELECT 1" &>/dev/null; then
    echo "✅ Root password is already set. Proceeding..."
else
    echo "⚠️ No root password detected or invalid. Attempting to set password..."

    if [ -z "$DB_ROOT_PASS" ]; then
        echo "❌ DB_ROOT_PASS is not set."
        exit 1
    fi

    sudo mariadb <<EOF
SET PASSWORD FOR 'root'@'localhost' = PASSWORD('$DB_ROOT_PASS');
FLUSH PRIVILEGES;
EOF

    if [ $? -ne 0 ]; then
        echo "❌ Failed to set root password."
        exit 1
    fi

    echo "✅ Root password successfully set."
fi

# Verify root password works
if ! mariadb -u root -p"$DB_ROOT_PASS" -e "SELECT 1" &>/dev/null; then
    echo "❌ Incorrect root password. Check the DB_ROOT_PASS variable."
    exit 1
fi

# Ensure required DB variables are set
if [ -z "$DB_NAME" ] || [ -z "$DB_USER" ]; then
    echo "❌ DB_NAME or DB_USER is not set."
    exit 1
fi

# If update is specified or mousetube_api isn't installed, (re)install it
if [ "$UPDATE" == true ] || ! python3 -c "import mousetube_api" &>/dev/null || ! python3 -c "import django" &>/dev/null; then
    echo "📦 mousetube_api not found or 'update' flag specified. Installing/reinstalling dependencies..."
    pip install --upgrade pip
    pip install -e .
else
    echo "✅ mousetube_api is already installed, skipping installation."
fi

# Load env variables from file if available
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

# Optionally load fixtures
if [ -f "$FIXTURE_FILE" ]; then
    echo "📦 Loading Django fixture from $FIXTURE_FILE..."
    python3 manage.py loaddata "$FIXTURE_FILE"
fi

# Collect static files in production mode
if [ "$DEBUG" == "false" ]; then
    echo "📦 Collecting static files..."
    python3 manage.py collectstatic --noinput
fi

# Start the server if "deploy" flag is set
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