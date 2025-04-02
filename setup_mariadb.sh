#!/bin/bash

# load maria_db from .env file
if [ -f mousetube.env ]; then
    export $(grep -v '^#' mousetube.env | xargs)
elif [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "No .env or mousetube.env file found!"
    exit 1
fi

# Execute Mariadb and create user
sudo mariadb -u root <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED BY '$DB_ROOT_PASS';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "Database $DB_NAME and user $DB_USER successfully created."