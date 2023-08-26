#! /usr/bin/env bash

# Run migrations
alembic upgrade head

if [ "${ENVIRONMENT}" = "development" ]; then
    echo "Environment is development, running poetry install"
    poetry install
fi

# Run the pre_start python script
python /app/app/backend_pre_start.py

