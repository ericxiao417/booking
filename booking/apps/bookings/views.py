"""
Views for the bookings app.
"""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)

from booking.apps.bookings.forms import BookingForm, BookingFilterForm
from booking.apps.bookings.models import Booking
from booking.apps.bookings.tasks import send_booking_confirmation, send_booking_cancellation
from booking.apps.facilities.models import Facility


class BookingListView(LoginRequiredMixin, ListView):
    """View for listing bookings."""
    model = Booking
    context_object_name = 'bookings'
    template_name = 'bookings/booking_list.html'
    paginate_by = 10
    
    def get_queryset(self):
        """Get filtered queryset for user's bookings."""
        # Staff can see all bookings, regular users only see their own
        if self.request.user.is_staff:
            queryset = Booking.objects.all()
        else:
            queryset = Booking.objects.filter(user=self.request.user)
        
        # Apply filters
        self.form = BookingFilterForm(self.request.GET or None)
        if self.form.is_valid():
            queryset = self.form.filter_queryset(queryset)
            
        return queryset.select_related('facility', 'user')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['form'] = self.form
        context['is_staff'] = self.request.user.is_staff
        return context


class BookingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """View for showing booking details."""
    model = Booking
    context_object_name = 'booking'
    template_name = 'bookings/booking_detail.html'
    
    def test_func(self):
        """Test if user can view this booking."""
        booking = self.get_object()
        # Staff can view all bookings, users can only view their own
        return self.request.user.is_staff or booking.user == self.request.user


class BookingCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new booking."""
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('bookings:booking_list')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = _('Create Booking')
        context['facility_id'] = self.request.GET.get('facility')
        
        # If facility_id is provided, get facility details
        if context['facility_id']:
            try:
                context['facility'] = Facility.objects.get(pk=context['facility_id'])
            except Facility.DoesNotExist:
                pass
                
        return context
    
    def get_form_kwargs(self):
        """Add user to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # Pre-select facility if provided in GET parameters
        facility_id = self.request.GET.get('facility')
        if facility_id and not kwargs.get('data'):
            kwargs['initial'] = kwargs.get('initial', {})
            kwargs['initial']['facility'] = facility_id
            
        return kwargs
    
    def form_valid(self, form):
        """Handle valid form."""
        # Set the user
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Send confirmation email as a background task
        send_booking_confirmation.delay(self.object.pk)
        
        messages.success(self.request, _('Booking created successfully.'))
        return response


class BookingUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating a booking."""
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/booking_form.html'
    
    def test_func(self):
        """Test if user can update this booking."""
        booking = self.get_object()
        # Check if the booking belongs to the user and is not cancelled
        return (booking.user == self.request.user and booking.status != 'cancelled')
    
    def get_context_data(self, **kwargs):
        """Add extra context data."""
        context = super().get_context_data(**kwargs)
        context['title'] = _('Update Booking')
        return context
    
    def get_form_kwargs(self):
        """Add user to form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_success_url(self):
        """Return the success URL."""
        messages.success(self.request, _('Booking updated successfully.'))
        return reverse_lazy('bookings:booking_detail', kwargs={'pk': self.object.pk})


class BookingCancelView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for cancelling a booking."""
    
    def test_func(self):
        """Test if user can cancel this booking."""
        booking = get_object_or_404(Booking, pk=self.kwargs.get('pk'))
        # User can cancel their own bookings if they're not already cancelled
        return (booking.user == self.request.user and booking.status != 'cancelled') or self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        booking = get_object_or_404(Booking, pk=kwargs.get('pk'))
        booking.cancel()
        
        # Send cancellation email as a background task
        send_booking_cancellation.delay(booking.pk)
        
        # If AJAX request, return JSON response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': _('Booking cancelled successfully.')
            })
        
        messages.success(request, _('Booking cancelled successfully.'))
        return redirect('bookings:booking_detail', pk=booking.pk)


class BookingConfirmView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for confirming a booking (staff only)."""
    
    def test_func(self):
        """Test if user can confirm this booking."""
        # Only staff can confirm bookings
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        booking = get_object_or_404(Booking, pk=kwargs.get('pk'))
        booking.confirm()
        
        # Send confirmation email as a background task
        send_booking_confirmation.delay(booking.pk)
        
        # If AJAX request, return JSON response
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': _('Booking confirmed successfully.')
            })
        
        messages.success(request, _('Booking confirmed successfully.'))
        return redirect('bookings:booking_detail', pk=booking.pk)


class BookingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a booking (staff only)."""
    model = Booking
    template_name = 'bookings/booking_confirm_delete.html'
    success_url = reverse_lazy('bookings:booking_list')
    
    def test_func(self):
        """Test if user can delete this booking."""
        # Only staff can delete bookings
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        """Handle the delete action."""
        messages.success(request, _('Booking deleted successfully.'))
        return super().delete(request, *args, **kwargs)
