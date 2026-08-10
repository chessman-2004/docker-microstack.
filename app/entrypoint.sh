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

# Run Alembic Database Migrations (Only executed on main app container startup)
if [ "$1" = "uvicorn" ]; then
  echo "🚀 Running Alembic database migrations..."
  alembic upgrade head
  echo "✅ Migrations complete!"
fi

echo "🚀 Launching application binary: $@"
exec "$@"