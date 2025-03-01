"""
URL configuration for booking project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from booking.apps.core.views import HomeView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Include app URLs
    path('accounts/', include('booking.apps.accounts.urls')),
    path('facilities/', include('booking.apps.facilities.urls')),
    path('bookings/', include('booking.apps.bookings.urls')),
    # Health check endpoint
    path('health/', include('health_check.urls')),
    # Home page
    path('', HomeView.as_view(), name='home'),
]

# Add debug toolbar for development
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
