#!/bin/bash
set -e

echo "===== Starting data import ====="

# Ensure database is ready
echo "Waiting for database..."
docker-compose exec -T web python manage.py wait_for_db

# Insert user data
echo "Inserting user data..."
docker-compose exec -T web python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# Create test users, all with password 'password123'
users_data = [
    {
        'username': 'john_smith', 
        'first_name': 'John', 
        'last_name': 'Smith', 
        'email': 'john.smith@example.com',
        'phone_number': '555-123-4567',
        'address': '123 Main St, New York, NY 10001'
    },
    {
        'username': 'sarah_johnson', 
        'first_name': 'Sarah', 
        'last_name': 'Johnson', 
        'email': 'sarah.johnson@example.com',
        'phone_number': '555-234-5678',
        'address': '456 Oak Ave, Los Angeles, CA 90001'
    },
    {
        'username': 'michael_brown', 
        'first_name': 'Michael', 
        'last_name': 'Brown', 
        'email': 'michael.brown@example.com',
        'phone_number': '555-345-6789',
        'address': '789 Elm St, Chicago, IL 60007'
    },
    {
        'username': 'emily_davis', 
        'first_name': 'Emily', 
        'last_name': 'Davis', 
        'email': 'emily.davis@example.com',
        'phone_number': '555-456-7890',
        'address': '101 Pine Rd, Houston, TX 77001'
    },
    {
        'username': 'david_wilson', 
        'first_name': 'David', 
        'last_name': 'Wilson', 
        'email': 'david.wilson@example.com',
        'phone_number': '555-567-8901',
        'address': '202 Cedar Blvd, Miami, FL 33101'
    }
]

for user_data in users_data:
    if not User.objects.filter(username=user_data['username']).exists():
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password='password123',
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            phone_number=user_data['phone_number'],
            address=user_data['address'],
            email_notifications=True,
            date_joined=timezone.now()
        )
        print(f'Created user: {user_data[\"username\"]}')
    else:
        print(f'User {user_data[\"username\"]} already exists')
"

# Insert facility data
echo "Inserting facility data..."
docker-compose exec -T db psql -U postgres -d booking -c "
INSERT INTO facilities_facility (name, location, capacity, description, image, is_active, opening_time, closing_time, created_at, updated_at)
VALUES
('Conference Room A', 'Main Building 1st Floor', 20, 'Standard conference room equipped with projector and electronic whiteboard', 'facilities/meeting_room_a.jpg', true, '08:00:00', '20:00:00', NOW(), NOW()),
('Conference Room B', 'Main Building 2nd Floor', 40, 'Large conference room suitable for department meetings and training sessions', 'facilities/meeting_room_b.jpg', true, '08:00:00', '20:00:00', NOW(), NOW()),
('Multipurpose Hall', 'Main Building Basement', 100, 'Multipurpose activity hall for lectures, seminars and events', 'facilities/multipurpose_hall.jpg', true, '09:00:00', '22:00:00', NOW(), NOW()),
('Fitness Center', 'Annex Building 1st Floor', 30, 'Equipped with treadmills, dumbbells and other fitness equipment', 'facilities/gym.jpg', true, '06:00:00', '22:00:00', NOW(), NOW()),
('Basketball Court', 'Outdoor Area', 20, 'Standard basketball court with lighting facilities', 'facilities/basketball_court.jpg', true, '07:00:00', '21:00:00', NOW(), NOW()),
('Badminton Court', 'Annex Building 2nd Floor', 16, '4 standard badminton courts', 'facilities/badminton_court.jpg', true, '07:00:00', '21:00:00', NOW(), NOW()),
('Library', 'Main Building 3rd Floor', 50, 'Quiet reading environment with extensive book collection', 'facilities/library.jpg', true, '08:00:00', '18:00:00', NOW(), NOW())
ON CONFLICT DO NOTHING;
"

# Insert booking data
echo "Inserting booking data..."
docker-compose exec -T db psql -U postgres -d booking -c "
INSERT INTO bookings_booking (user_id, facility_id, title, description, start_time, end_time, status, number_of_people, created_at, updated_at)
VALUES
((SELECT id FROM accounts_user WHERE username='john_smith' LIMIT 1), (SELECT id FROM facilities_facility WHERE name='Conference Room A' LIMIT 1), 'Project Kickoff Meeting', 'Discuss new project launch plan and task assignments', NOW() + INTERVAL '1 day', NOW() + INTERVAL '1 day 2 hours', 'confirmed', 8, NOW(), NOW()),
((SELECT id FROM accounts_user WHERE username='sarah_johnson' LIMIT 1), (SELECT id FROM facilities_facility WHERE name='Conference Room B' LIMIT 1), 'Department Quarterly Meeting', 'Review current quarter work and next quarter planning', NOW() + INTERVAL '2 days', NOW() + INTERVAL '2 days 3 hours', 'confirmed', 25, NOW(), NOW()),
((SELECT id FROM accounts_user WHERE username='michael_brown' LIMIT 1), (SELECT id FROM facilities_facility WHERE name='Multipurpose Hall' LIMIT 1), 'Tech Sharing Session', 'Sharing and exchange of cutting-edge technologies', NOW() + INTERVAL '5 days', NOW() + INTERVAL '5 days 4 hours', 'pending', 60, NOW(), NOW()),
((SELECT id FROM accounts_user WHERE username='emily_davis' LIMIT 1), (SELECT id FROM facilities_facility WHERE name='Basketball Court' LIMIT 1), 'Department Basketball Game', 'Friendly basketball match to enhance team cohesion', NOW() + INTERVAL '3 days', NOW() + INTERVAL '3 days 2 hours', 'confirmed', 15, NOW(), NOW()),
((SELECT id FROM accounts_user WHERE username='david_wilson' LIMIT 1), (SELECT id FROM facilities_facility WHERE name='Badminton Court' LIMIT 1), 'Badminton Training', 'Regular training for company badminton team', NOW() + INTERVAL '4 days', NOW() + INTERVAL '4 days 1.5 hours', 'confirmed', 8, NOW(), NOW()),
((SELECT id FROM accounts_user WHERE username='john_smith' LIMIT 1), (SELECT id FROM facilities_facility WHERE name='Library' LIMIT 1), 'Book Club', 'Discussion on \"The 7 Habits of Highly Effective People\"', NOW() + INTERVAL '7 days', NOW() + INTERVAL '7 days 2 hours', 'pending', 12, NOW(), NOW()),
((SELECT id FROM accounts_user WHERE username='sarah_johnson' LIMIT 1), (SELECT id FROM facilities_facility WHERE name='Fitness Center' LIMIT 1), 'Team Fitness Activity', 'Team activity promoting healthy lifestyle', NOW() + INTERVAL '6 days', NOW() + INTERVAL '6 days 1 hour', 'cancelled', 10, NOW(), NOW())
ON CONFLICT DO NOTHING;
"

echo "===== Data import completed ====="