#!/bin/sh
set -e

# Create data dir and set ownership (runs as root)
mkdir -p /app/data
chown -R appuser:appuser /app

# Switch to appuser and run the main command
exec su-exec appuser "$@"