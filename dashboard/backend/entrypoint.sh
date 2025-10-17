#!/bin/sh
set -e

# Run as root: Create data dir and set ownership only on the volume
mkdir -p /app/data
chown -R appuser:appuser /app/data

# Switch to appuser and exec the command
exec su-exec appuser "$@"