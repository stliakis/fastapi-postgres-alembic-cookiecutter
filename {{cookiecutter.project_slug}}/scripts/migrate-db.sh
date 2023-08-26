#! /usr/bin/env bash

docker-compose exec backend alembic revision --autogenerate -m "$1"
docker-compose exec backend alembic upgrade head