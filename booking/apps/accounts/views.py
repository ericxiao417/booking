"""
Account views for the booking project.
"""
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView, UpdateView

from booking.apps.accounts.forms import SignUpForm, ProfileUpdateForm
from booking.apps.accounts.models import User


class SignUpView(CreateView):
    """View to register a new user."""
    model = User
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')
    
    def form_valid(self, form):
        """Log in the user after successful registration."""
        response = super().form_valid(form)
        # Log in the user
        login(self.request, self.object)
        messages.success(
            self.request, 
            _('Welcome to Booking System! Your account has been created.')
        )
        return response


class CustomLoginView(LoginView):
    """Customized login view."""
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Add success message on login."""
        messages.info(self.request, _('You have successfully logged in.'))
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    """Customized logout view."""
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        """Add success message on logout."""
        if request.user.is_authenticated:
            messages.info(request, _('You have been logged out.'))
        return super().dispatch(request, *args, **kwargs)


class ProfileDetailView(LoginRequiredMixin, DetailView):
    """View to display user profile."""
    model = User
    template_name = 'accounts/profile_detail.html'
    context_object_name = 'profile_user'
    
    def get_object(self, queryset=None):
        """Return the current user's profile."""
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """View to update user profile."""
    model = User
    form_class = ProfileUpdateForm
    template_name = 'accounts/profile_update.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        """Return the current user's profile."""
        return self.request.user
    
    def form_valid(self, form):
        """Add success message on profile update."""
        messages.success(self.request, _('Your profile has been updated.'))
        return super().form_valid(form)


@login_required
def change_password(request):
    """View to change user password."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in
            update_session_auth_hash(request, user)
            messages.success(request, _('Your password has been changed.'))
            return redirect('accounts:profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/password_change.html', {'form': form})