"""
Facility models for the booking project.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Facility(models.Model):
    """
    Facility model to represent bookable spaces/resources.
    """
    name = models.CharField(_('name'), max_length=100)
    location = models.CharField(_('location'), max_length=200)
    capacity = models.PositiveIntegerField(_('capacity'))
    description = models.TextField(_('description'), blank=True)
    image = models.ImageField(_('image'), upload_to='facilities/', blank=True, null=True)
    is_active = models.BooleanField(_('active'), default=True)
    
    # Opening hours (can be enhanced with more detailed scheduling)
    opening_time = models.TimeField(_('opening time'), null=True, blank=True)
    closing_time = models.TimeField(_('closing time'), null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        """Meta options for the Facility model."""
        verbose_name = _('facility')
        verbose_name_plural = _('facilities')
        ordering = ['name']
        # Database optimization - add indexes
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        """Return string representation."""
        return self.name
    
    def get_available_slots(self, date):
        """
        Get available time slots for a specific date.
        This is a placeholder method that will be implemented with actual business logic.
        """
        # This would be implemented to check bookings and return available slots
        return []
    
    def is_available(self, start_time, end_time):
        """
        Check if facility is available for a given time range.
        """
        from booking.apps.bookings.models import Booking
        # Check if there are any overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            facility=self,
            status='confirmed',
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()
        
        return not overlapping_bookings