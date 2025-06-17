#!/bin/bash
set -e

# Function to wait for a service
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    
    echo "Waiting for $service to be ready..."
    while ! nc -z $host $port; do
        sleep 1
    done
    echo "$service is ready!"
}

# Wait for optional services if enabled
if [ "$USE_POSTGRES" = "true" ]; then
    wait_for_service ${DB_HOST:-postgres} ${DB_PORT:-5432} "PostgreSQL"
fi

if [ "$USE_REDIS" = "true" ]; then
    wait_for_service ${REDIS_HOST:-redis} ${REDIS_PORT:-6379} "Redis"
fi

# Run migrations if needed
if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running database migrations..."
    python -m scripts.migrate
fi

# Validate configuration
echo "Validating configuration..."
python manage.py validate

# Execute the main command
exec "$@"