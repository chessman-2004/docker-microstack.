# ==========================================
# STAGE 1: Build Dependencies
# ==========================================
FROM python:3.11-alpine AS builder

WORKDIR /build

# Install build dependencies required for compiling psycopg2 and C extensions
# hadolint ignore=DL3018
RUN apk add --no-cache gcc musl-dev postgresql-dev libffi-dev

COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# STAGE 2: Final Minimal Runtime Image
# ==========================================
FROM python:3.11-alpine

WORKDIR /app

# Install runtime PostgreSQL client library & netcat for entrypoint health checks
# hadolint ignore=DL3018
RUN apk add --no-cache libpq netcat-openbsd

# Create a non-root group and user with explicit numeric IDs (UID/GID 10001)
RUN addgroup -g 10001 -S appgroup && adduser -u 10001 -S appuser -G appgroup

# Copy built Python packages from builder stage
COPY --from=builder /install /usr/local

# 1. Copy application source code, migrations, and alembic.ini configuration
COPY app/ .
COPY alembic/ ./alembic/
COPY alembic.ini /app/alembic.ini

# Make entrypoint script executable and set ownership
RUN mkdir -p /app/generated_pdfs && \
    chmod +x /app/entrypoint.sh && \
    chown -R appuser:appgroup /app

# Use numeric UID for security & Hadolint compliance
USER 10001

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]