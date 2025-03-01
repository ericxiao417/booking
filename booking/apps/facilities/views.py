"""
Views for the facilities app.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from booking.apps.facilities.forms import FacilityFilterForm, FacilityForm
from booking.apps.facilities.models import Facility


class FacilityListView(ListView):
    """View for listing facilities."""
    model = Facility
    context_object_name = 'facilities'
    template_name = 'facilities/facility_list.html'
    paginate_by = 10
    
    def get_queryset(self):
        """Get filtered queryset."""
        queryset = Facility.objects.filter(is_active=True)
        self.form = FacilityFilterForm(self.request.GET or None)
        
        if self.form.is_valid():
            queryset = self.form.filter_queryset(queryset)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        return context


class FacilityDetailView(DetailView):
    """View for showing facility details."""
    model = Facility
    context_object_name = 'facility'
    template_name = 'facilities/facility_detail.html'


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff access."""
    
    def test_func(self):
        """Test if user is staff."""
        return self.request.user.is_staff


class FacilityCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """View for creating a new facility."""
    model = Facility
    form_class = FacilityForm
    template_name = 'facilities/facility_form.html'
    success_url = reverse_lazy('facilities:facility_list')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create Facility')
        return context
    
    def form_valid(self, form):
        """Handle valid form."""
        messages.success(self.request, _('Facility created successfully.'))
        return super().form_valid(form)


class FacilityUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """View for updating a facility."""
    model = Facility
    form_class = FacilityForm
    template_name = 'facilities/facility_form.html'
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = _('Update Facility')
        return context
    
    def get_success_url(self):
        """Return the success URL."""
        messages.success(self.request, _('Facility updated successfully.'))
        return reverse_lazy('facilities:facility_detail', kwargs={'pk': self.object.pk})


class FacilityDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    """View for deleting a facility."""
    model = Facility
    template_name = 'facilities/facility_confirm_delete.html'
    success_url = reverse_lazy('facilities:facility_list')
    
    def delete(self, request, *args, **kwargs):
        """Handle the delete action."""
        messages.success(request, _('Facility deleted successfully.'))
        return super().delete(request, *args, **kwargs)
