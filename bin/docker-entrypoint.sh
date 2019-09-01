#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py db upgrade

# Start server
echo "Starting server"
honcho start