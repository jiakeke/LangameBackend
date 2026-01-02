#!/bin/sh
set -e

echo "Starting Django container..."

# ---- 1. 等待数据库 ----
echo "Waiting for database at $DB_HOST:$DB_PORT..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done

echo "Database is available"

# ---- 2. Django 初始化 ----
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# ---- 3. 启动 Gunicorn（非常关键）----
echo "Starting Gunicorn..."
exec gunicorn langame.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
