# Stage 1: Build stage
FROM python:3.10-alpine AS builder

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    curl \
    libjpeg-turbo-dev \
    zlib-dev \
    libpng-dev \
    poppler-utils

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.10-alpine

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies only
RUN apk add --no-cache \
    libjpeg-turbo \
    zlib \
    libpng \
    poppler-utils \
    && rm -rf /var/cache/apk/*

# Copy installed Python dependencies from builder stage to a system-wide location
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code
COPY . .

# Create appuser and set permissions for /app and /data
RUN adduser -D appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /app /data

USER appuser

# Expose the port used in CMD
EXPOSE 18889

# Command to run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "18889"]