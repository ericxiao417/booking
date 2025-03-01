"""
Account forms for the booking project.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from booking.apps.accounts.models import User


class SignUpForm(UserCreationForm):
    """Form for user registration."""
    
    email = forms.EmailField(
        max_length=254, 
        required=True, 
        help_text=_('Required. Enter a valid email address.')
    )
    
    phone_number = forms.CharField(
        max_length=20, 
        required=False, 
        help_text=_('Optional. Enter your phone number.')
    )
    
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text=_('Required. Enter your first name.')
    )
    
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        help_text=_('Required. Enter your last name.')
    )
    
    class Meta:
        """Meta options."""
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'password1', 'password2'
        ]


class LoginForm(AuthenticationForm):
    """Form for user login."""
    
    remember_me = forms.BooleanField(
        required=False, 
        initial=False, 
        widget=forms.CheckboxInput()
    )
    
    class Meta:
        """Meta options."""
        model = User
        fields = ['username', 'password', 'remember_me']


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile."""
    
    class Meta:
        """Meta options."""
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'address', 'profile_picture', 'email_notifications'
        ]
        
    def __init__(self, *args, **kwargs):
        """Initialize the form."""
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
