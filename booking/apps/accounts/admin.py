"""
Admin configuration for the accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from booking.apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Admin configuration for the custom User model."""
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_picture')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Settings'), {'fields': ('email_notifications',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    list_display = [
        'username', 'email', 'first_name', 'last_name', 'phone_number', 
        'is_staff', 'is_active'
    ]
    
    list_filter = DjangoUserAdmin.list_filter + ('email_notifications',)
    search_fields = DjangoUserAdmin.search_fields + ('phone_number', 'address')
