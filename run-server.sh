#!/bin/bash

source .venv/bin/activate
cd pollrss

# Check for a django secret
if [ ! -f django_secret ]; then
    echo "Secret not found. Generating a new one..."

    # Generate a new django secret
    secret_key=$(head /dev/urandom | tr -dc A-Za-z0-9 | head -c50)
    echo "$secret_key" > django_secret
fi

# Read secret from file
secret_key=$(cat "django_secret")
export DJANGO_SECRET_KEY="$secret_key"

# Check if running in DEBUG or PROD
if [ "$1" = "DEBUG" ]; then
    export DJANGO_DEBUG=True
fi

# Check if running LOCAL or REMOTE
if [[ "$1" = "REMOTE" || "$2" = "REMOTE" ]]; then
    # POSTGRES Configuration
    export DJANGO_DB_ENGINE=django.db.backends.postgresql
    export DJANGO_DB_HOST=192.168.1.110
    export DJANGO_DB_PORT=5432
    export DJANGO_DB_NAME=db_pollrss
    export DJANGO_DB_USER=user_pollrss
    export DJANGO_DB_PASSWORD=pollrss

else
    export DJANGO_DB_ENGINE=django.db.backends.sqlite3
    export DJANGO_DB_NAME=db_pollrss

fi

# Check for migration commands
if [ "$1" = "RUN" ]; then
    $2
else
    # Run Gunicorn
    gunicorn pollrss.wsgi

fi
