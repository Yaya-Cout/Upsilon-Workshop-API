#!/usr/bin/sh
# Script to prepare a run of the application
echo "Preparing run..."

# Create the database/update it
python3 manage.py migrate

echo "Run prepared! Starting server..."
