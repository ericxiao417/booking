"""
Django command to initialize the database, and create it if it doesn't exist
"""
import os
import time
import subprocess
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.utils import OperationalError, ProgrammingError


class Command(BaseCommand):
    """Initialize database command"""
    
    help = 'Ensure the database exists and is available'

    def handle(self, *args, **options):
        self.stdout.write('Checking if database exists...')
        
        db_name = os.environ.get('POSTGRES_DB', 'booking')
        db_user = os.environ.get('POSTGRES_USER', 'postgres')
        db_password = os.environ.get('POSTGRES_PASSWORD', 'postgres')
        db_host = os.environ.get('POSTGRES_HOST', 'db')
        
        # Try to run a simple query to check if the database exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            self.stdout.write(self.style.SUCCESS(f'Database {db_name} already exists and is available!'))
            return
        except (OperationalError, ProgrammingError) as e:
            self.stdout.write(self.style.WARNING(f'Database access error: {e}'))
            self.stdout.write('Attempting to create database...')
        
        # Try to create the database using psql command
        try:
            # First connect to the default postgres database
            create_db_cmd = [
                'psql', 
                '-h', db_host, 
                '-U', db_user, 
                '-c', f"CREATE DATABASE {db_name};"
            ]
            
            # Set the PGPASSWORD environment variable
            env = os.environ.copy()
            env['PGPASSWORD'] = db_password
            
            result = subprocess.run(
                create_db_cmd, 
                env=env,
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                self.stdout.write(self.style.SUCCESS(f'Successfully created database {db_name}!'))
            else:
                self.stdout.write(self.style.WARNING(f'Failed to create database: {result.stderr}'))
                if "already exists" in result.stderr:
                    self.stdout.write(self.style.SUCCESS('Database already exists, continuing...'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating database: {e}'))
            self.stdout.write(self.style.WARNING('Attempting to continue, hoping the database already exists...'))
