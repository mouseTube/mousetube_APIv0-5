#!/bin/bash

# Load MariaDB variables from the environment file
if [ -f mousetube.env ]; then
    export $(grep -v '^#' mousetube.env | xargs)
elif [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env or mousetube.env file found!"
    exit 1
fi

# Check if MariaDB root access is available without a password
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

# Verify if root access with the password works
if ! mysql -u root -p"$DB_ROOT_PASS" -e "SELECT 1" &>/dev/null; then
    echo "❌ Incorrect root password. Check the DB_ROOT_PASS variable."
    exit 1
fi

# Ask for confirmation before modifying the database
echo "⚠️  This operation will delete and recreate the database '$DB_NAME'. Continue? (y/n)"
read CONFIRM
if [ "$CONFIRM" != "y" ]; then
    echo "❌ Operation canceled."
    exit 1
fi

# Execute MariaDB commands to set up the database and user
echo "🚀 Configuring the database..."
sudo mariadb -u root -p"$DB_ROOT_PASS" <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASS';
FLUSH PRIVILEGES;
DROP DATABASE $DB_NAME;
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

# Check if the database setup was successful
if [ $? -ne 0 ]; then
    echo "❌ Error configuring the database."
    exit 1
fi

# Check if the SQL file exists before importing data
if [ -f "$SQL_FILE" ]; then
    echo "📂 Importing data from $SQL_FILE..."
    mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$SQL_FILE"
    
    # Check if data import was successful
    if [ $? -eq 0 ]; then
        echo "✅ Data successfully imported!"
    else
        echo "❌ Error importing SQL file."
        exit 1
    fi
else
    echo "⚠️  Warning: SQL file '$SQL_FILE' not found. The database is empty but ready to use."
fi

echo "✅ Database '$DB_NAME' and user '$DB_USER' successfully created!"