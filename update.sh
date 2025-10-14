#!/bin/bash
set -e

# --- Resolve absolute paths based on script location ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"
FRONTEND_DIR="$SCRIPT_DIR/../mousetube_frontendv0-5"

echo "🔄 Updating backend..."
cd "$BACKEND_DIR"
git pull origin main

echo "🔄 Updating frontend..."
cd "$FRONTEND_DIR"
git pull origin main

echo "🐳 Rebuilding and restarting Docker containers..."
cd "$BACKEND_DIR"

# Rebuild images if Dockerfile or dependencies changed
docker-compose build web frontend

# Restart web and frontend services
docker-compose up -d web frontend

echo "🗂️ Applying Django migrations..."
docker-compose run --rm web python /app/manage.py migrate

echo "✅ Backend and frontend updated and restarted!"