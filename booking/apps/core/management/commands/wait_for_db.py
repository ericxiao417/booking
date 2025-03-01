"""
Django command to wait for the database to be available.
"""
import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError
import subprocess


class Command(BaseCommand):
    """Wait for database to be available and ensure database exists"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_up = False
        while not db_up:
            try:
                # Try to get database connection
                self.check_database()
                db_up = True
            except (OperationalError, Psycopg2OpError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
    
    def check_database(self):
        """Check database connection, try to create database if it doesn't exist"""
        conn = connections['default']
        conn.ensure_connection()
        
        # If code execution reaches here, it means connection is successful
        # But this doesn't guarantee the database exists, so we need to execute a query
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return True
