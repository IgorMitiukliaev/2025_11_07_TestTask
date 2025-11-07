#!/bin/bash
cd /opt
# apply database migrations
poetry run alembic upgrade head


# poetry run python -m db.init_db
# start the application 
# poetry run uvicorn main:app --host 0.0.0.0 --port $APP_PORT --log-level 'debug' --workers=1
poetry run python -m main