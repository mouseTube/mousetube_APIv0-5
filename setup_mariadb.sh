#!/bin/bash

FIXTURE_FILE=./exported_data.json

echo "Fixture file to load: $FIXTURE_FILE"

# Load MariaDB variables from the environment file
if [ -f mousetube.env ]; then
    export $(grep -v '^#' mousetube.env | xargs)
elif [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env or mousetube.env file found!"
    exit 1
fi

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

echo "⚠️  This operation will delete and recreate the database '$DB_NAME'. Continue? (y/n)"
read CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ Operation canceled."
    exit 1
fi

echo "🚀 Configuring the database..."
sudo mariadb -u root -p"$DB_ROOT_PASS" <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASS';
FLUSH PRIVILEGES;
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

echo "🐍 Running Django migrations..."
python3 manage.py makemigrations mousetube_api --noinput
python3 manage.py migrate --noinput


# Option : load Django fixtures (.json)
if [ -f "$FIXTURE_FILE" ]; then
    echo "📦 Loading Django fixture from $FIXTURE_FILE..."
    python3 manage.py loaddata "$FIXTURE_FILE"
fi

echo "✅ Database '$DB_NAME' successfully migrated and ready!"