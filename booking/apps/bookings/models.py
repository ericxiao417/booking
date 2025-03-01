"""
Booking models for the booking project.
"""
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Booking(models.Model):
    """
    Booking model to represent reservations for facilities.
    """
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
    )
    
    # Relations
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('user')
    )
    facility = models.ForeignKey(
        'facilities.Facility', 
        on_delete=models.CASCADE,
        related_name='bookings',
        verbose_name=_('facility')
    )
    
    # Booking details
    title = models.CharField(_('title'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    start_time = models.DateTimeField(_('start time'))
    end_time = models.DateTimeField(_('end time'))
    status = models.CharField(
        _('status'),
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    number_of_people = models.PositiveIntegerField(_('number of people'), default=1)
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        """Meta options for the Booking model."""
        verbose_name = _('booking')
        verbose_name_plural = _('bookings')
        ordering = ['-start_time']
        # Database optimization - add indexes
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['facility']),
            models.Index(fields=['status']),
            models.Index(fields=['start_time', 'end_time']),
        ]
        # Add constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F('start_time')),
                name='end_time_after_start_time'
            ),
        ]
    
    def __str__(self):
        """Return string representation."""
        return f"{self.title} - {self.facility.name} ({self.start_time.strftime('%Y-%m-%d %H:%M')})"
    
    def clean(self):
        """Validate booking data."""
        # Check if end_time is after start_time
        if self.end_time <= self.start_time:
            raise ValidationError(_('End time must be after start time.'))
        
        # Check if start_time is in the future for new bookings
        if not self.pk and self.start_time < timezone.now():
            raise ValidationError(_('Start time must be in the future.'))
        
        # Check facility capacity
        if self.number_of_people > self.facility.capacity:
            raise ValidationError(
                _('Number of people exceeds facility capacity of %(capacity)s.'),
                params={'capacity': self.facility.capacity},
            )
        
        # Check for availability
        if not self.is_facility_available():
            raise ValidationError(_('The facility is not available during the selected time period.'))
    
    def is_facility_available(self):
        """Check if the facility is available for this booking."""
        if not self.pk:  # New booking
            return self.facility.is_available(self.start_time, self.end_time)
        else:  # Existing booking
            overlapping_bookings = Booking.objects.filter(
                facility=self.facility,
                status='confirmed',
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(pk=self.pk).exists()
            return not overlapping_bookings
    
    def confirm(self):
        """Confirm the booking."""
        self.status = 'confirmed'
        self.save()
    
    def cancel(self):
        """Cancel the booking."""
        self.status = 'cancelled'
        self.save()