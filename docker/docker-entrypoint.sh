#!/bin/sh

# collectstatic files
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Start server
echo "Starting server"
daphne -b 0.0.0.0 -p 8000 ghablameh.asgi:application
