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
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final stage
FROM python:3.10-alpine

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install runtime dependencies (including su-exec for entrypoint)
RUN apk add --no-cache \
    libjpeg-turbo \
    zlib \
    libpng \
    poppler-utils \
    su-exec \
    && rm -rf /var/cache/apk/*

# Create appuser early
RUN adduser -D appuser

# Copy installed Python dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Set ownership on user deps at build time (as root)
RUN chown -R appuser:appuser /home/appuser

# Copy the application code (including entrypoint.sh)
COPY . .

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Install uvicorn system-wide (as root)
RUN pip install uvicorn

# Set PATH for appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

# Entrypoint runs as root, then switches user
ENTRYPOINT ["/app/entrypoint.sh"]

USER appuser

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]