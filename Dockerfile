# ==========================================
# STAGE 1: Build Dependencies
# ==========================================
FROM python:3.11-alpine AS builder

WORKDIR /build

# hadolint ignore=DL3018
RUN apk add --no-cache gcc musl-dev

# Install dependencies into a temporary directory
COPY app/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ==========================================
# STAGE 2: Final Minimal Runtime Image
# ==========================================
FROM python:3.11-alpine

WORKDIR /app

# Create a non-root group and user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Copy built Python packages from the builder stage
COPY --from=builder /install /usr/local

# Copy application source code
COPY app/ .

# Change ownership of app files to non-root user
RUN chown -R appuser:appgroup /app

# hadolint ignore=DL3066
USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]