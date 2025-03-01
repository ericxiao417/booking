"""
Core views for the booking project.
"""
from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Welcome to Booking System'
        return context
