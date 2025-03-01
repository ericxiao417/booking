"""
Admin configuration for the bookings app.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from booking.apps.bookings.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for the Booking model."""
    list_display = [
        'title', 'facility', 'user', 'start_time', 'end_time', 
        'status', 'number_of_people', 'created_at'
    ]
    list_filter = ['status', 'facility', 'start_time']
    search_fields = ['title', 'description', 'user__username', 'user__email', 'facility__name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_time'
    actions = ['confirm_bookings', 'cancel_bookings']
    
    fieldsets = (
        (None, {
            'fields': ('user', 'facility', 'title', 'description')
        }),
        (_('Booking Details'), {
            'fields': ('start_time', 'end_time', 'number_of_people', 'status')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def confirm_bookings(self, request, queryset):
        """Admin action to confirm selected bookings."""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(
            request,
            _('%(count)d booking(s) were successfully confirmed.') % {'count': updated}
        )
    confirm_bookings.short_description = _('Confirm selected bookings')
    
    def cancel_bookings(self, request, queryset):
        """Admin action to cancel selected bookings."""
        updated = queryset.exclude(status='cancelled').update(status='cancelled')
        self.message_user(
            request,
            _('%(count)d booking(s) were successfully cancelled.') % {'count': updated}
        )
    cancel_bookings.short_description = _('Cancel selected bookings')
