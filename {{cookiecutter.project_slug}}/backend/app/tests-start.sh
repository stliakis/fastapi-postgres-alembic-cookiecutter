#! /usr/bin/env bash
set -e

export ENVIRONMENT=testing
export DEBUG_USER=None

python /app/app/tests_pre_start.py

bash ./scripts/test.sh "$@"
