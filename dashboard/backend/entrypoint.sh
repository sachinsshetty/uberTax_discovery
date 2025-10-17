#!/bin/sh
set -e

# Run as root: Create data dir and set ownership only on writable paths
mkdir -p /app/data
chown -R appuser:appuser /app/data /home/appuser

# Switch to appuser and exec the command (inherits ENV PATH)
exec su-exec appuser "$@"