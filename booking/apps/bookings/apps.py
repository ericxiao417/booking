"""
Bookings app configuration.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BookingsConfig(AppConfig):
    """Bookings app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking.apps.bookings'
    verbose_name = _('Bookings')
