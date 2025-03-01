#!/bin/bash
set -e

# Down all containers and remove volumes
echo "Stopping and removing containers..."
docker-compose down -v

# Remove old images
echo "Pruning unused Docker resources..."
docker system prune -a -f

# Build and start the containers
echo "Building and starting containers..."
docker-compose build --no-cache
docker-compose up -d

# Wait for services to start
echo "Waiting for services to initialize (15 seconds)..."
sleep 15

# Check web container status
WEB_STATUS=$(docker inspect --format='{{.State.Status}}' booking-web-1 2>/dev/null || echo "not_found")
if [ "$WEB_STATUS" != "running" ]; then
    echo "Web container is not running. Checking logs..."
    docker logs booking-web-1
    
    echo "Trying to restart web container..."
    docker-compose restart web
    
    echo "Waiting for web container to restart (10 seconds)..."
    sleep 10
fi

# Ensure database exists
echo "Ensuring database exists..."
docker-compose exec -T db psql -U postgres -c "CREATE DATABASE booking;" || echo "Database may already exist"

# Wait a bit more for DB to be ready
echo "Waiting for database to be fully ready (5 seconds)..."
sleep 5

# Apply migrations
echo "Applying migrations..."
docker-compose exec -T web python manage.py migrate || echo "Migration might have already been applied"

# Create superuser
echo "Creating superuser..."
docker-compose exec -T web python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')" || echo "Could not create superuser, will need to be created manually"

docker-compose exec -T web bash -c "
  mkdir -p /app/booking/apps
  touch /app/booking/apps/__init__.py
  touch /app/booking/apps/bookings/__init__.py
  touch /app/booking/apps/facilities/__init__.py
  touch /app/booking/apps/accounts/__init__.py
  touch /app/booking/apps/core/__init__.py
"

echo "Project initialization complete!"
echo "You can now access the application at: http://localhost:8000 or http://localhost"
echo "Admin credentials: username: admin, password: admin"
echo "If you still see an error, you may need to manually check the logs:"
echo "docker logs booking-web-1"
echo "Done!"