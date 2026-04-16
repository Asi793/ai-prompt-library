#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until python -c "
import psycopg2, os
psycopg2.connect(
    host=os.environ['POSTGRES_HOST'],
    port=os.environ['POSTGRES_PORT'],
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ['POSTGRES_PASSWORD']
)
" 2>/dev/null; do
    echo "  PostgreSQL not ready yet, retrying in 1s..."
    sleep 1
done
echo "PostgreSQL is ready."

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

exec gunicorn ai-prompt-library.wsgi:application --bind 0.0.0.0:$PORT
