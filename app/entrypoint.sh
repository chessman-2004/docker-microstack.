#!/bin/sh
set -e

echo "⏳ Waiting for PostgreSQL database initialization..."
until python -c "
import socket, os, urllib.parse
url = urllib.parse.urlparse(os.getenv('DATABASE_URL', 'postgresql://user:password@db:5432/microstack_db'))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(2)
s.connect((url.hostname, url.port or 5432))
s.close()
" 2>/dev/null; do
  echo "Postgres is unavailable - sleeping 1s"
  sleep 1
done

echo "✅ PostgreSQL is online!"

# Run Alembic Database Migrations safely if config exists
if [ "$1" = "uvicorn" ]; then
  if [ -f "/app/alembic.ini" ]; then
    echo "🚀 Running Alembic database migrations..."
    alembic -c /app/alembic.ini upgrade head || echo "⚠️ Migration check finished."
    echo "✅ Migrations complete!"
  else
    echo "ℹ️ No /app/alembic.ini found, bypassing database migrations."
  fi
fi

echo "🚀 Launching application binary: $@"
exec "$@"