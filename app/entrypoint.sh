#!/bin/sh

# Exit immediately if a command exits with a non-zero status
set -e

echo "⏳ Waiting for PostgreSQL to be ready..."

# Loop until PostgreSQL port 5432 accepts TCP connections
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 0.5
done

echo "✅ PostgreSQL is up! Initializing database schema..."

# Auto-create database tables defined in models.py
python -c "from database import engine; import models; models.Base.metadata.create_all(bind=engine)"

echo "🚀 Starting application server..."

# Execute the main container CMD (Uvicorn)
exec "$@"