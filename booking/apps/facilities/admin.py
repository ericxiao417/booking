"""
Admin configuration for the facilities app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from booking.apps.facilities.models import Facility


@admin.register(Facility)
class FacilityAdmin(admin.ModelAdmin):
    """Admin configuration for the Facility model."""
    list_display = ['name', 'location', 'capacity', 'is_active', 'opening_time', 'closing_time']
    list_filter = ['is_active', 'location']
    search_fields = ['name', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'location', 'capacity', 'description', 'image')
        }),
        (_('Availability'), {
            'fields': ('is_active', 'opening_time', 'closing_time')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )