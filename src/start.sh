#!/bin/bash
PROJECT_ROOT=/opt poetry run alembic upgrade head
# add initial data to tables from SQL scripts
# PROJECT_ROOT=/opt poetry run python -m db.init_db
# start the application 
# PROJECT_ROOT=/opt poetry run uvicorn main:app --host 0.0.0.0 --port $APP_PORT --log-level 'debug' --workers=1
PROJECT_ROOT=/opt poetry run python -m main