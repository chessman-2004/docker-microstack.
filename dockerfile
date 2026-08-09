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

# Create a non-root group and user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy built Python packages from builder stage
COPY --from=builder /install /usr/local

# Copy application source code and entrypoint script
COPY app/ .

# Make entrypoint script executable and set ownership
RUN chmod +x /app/entrypoint.sh && \
    chown -R appuser:appgroup /app

# hadolint ignore=DL3066
USER appuser

EXPOSE 8000

# Set entrypoint script to run before Uvicorn
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command executed by entrypoint.sh
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]