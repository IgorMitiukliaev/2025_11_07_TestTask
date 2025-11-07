#!/bin/bash
set -e

cd /opt

echo "Applying database migrations..."
poetry run alembic upgrade head

echo "Starting application..."
poetry run python -m main
