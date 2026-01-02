#!/bin/sh
set -e

# 等待 Postgres
if [ -n "$DB_HOST" ]; then
  echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 1
  done
  echo "PostgreSQL is up."
fi

exec "$@"
