"""
Facilities app configuration.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FacilitiesConfig(AppConfig):
    """Facilities app configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking.apps.facilities'
    verbose_name = _('Facilities')
