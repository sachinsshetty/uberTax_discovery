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

# Copy installed Python dependencies from builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Copy the application code (including entrypoint.sh)
COPY . .

# Create appuser
RUN adduser -D appuser

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Install uvicorn system-wide (as root)
RUN pip install uvicorn

# Switch to appuser and update PATH
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

EXPOSE 80

# Set entrypoint and default command
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]