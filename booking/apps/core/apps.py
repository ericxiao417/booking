"""
Core app configuration.
"""
from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core app configuration."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking.apps.core'
    verbose_name = 'Core'
