"""
Account models for the booking project.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for the booking project."""
    
    # Additional fields
    phone_number = models.CharField(_('phone number'), max_length=20, blank=True)
    address = models.TextField(_('address'), blank=True)
    
    # Profile picture
    profile_picture = models.ImageField(
        _('profile picture'), 
        upload_to='profiles/', 
        blank=True, 
        null=True
    )
    
    # User settings
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    
    class Meta:
        """Meta options."""
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def __str__(self):
        """Return string representation."""
        return self.username
    
    def get_full_name(self):
        """Return full name."""
        full_name = super().get_full_name()
        return full_name or self.username
