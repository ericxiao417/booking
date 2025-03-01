"""
Forms for the bookings app.
"""
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field

from booking.apps.bookings.models import Booking
from booking.apps.facilities.models import Facility


class BookingForm(forms.ModelForm):
    """Form for creating and updating bookings."""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter active facilities only
        self.fields['facility'].queryset = Facility.objects.filter(is_active=True)
        
        # Use better widgets for datetime fields
        self.fields['start_time'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        self.fields['end_time'].widget = forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        )
        
        # Set initial values for datetime fields
        if not self.instance.pk:
            now = timezone.now()
            # Round to next hour
            start = now.replace(minute=0, second=0, microsecond=0) + timezone.timedelta(hours=1)
            self.fields['start_time'].initial = start
            self.fields['end_time'].initial = start + timezone.timedelta(hours=1)
            
        # Setup Crispy form layout
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('facility'),
            Field('title'),
            Row(
                Column('start_time', css_class='form-group col-md-6'),
                Column('end_time', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('number_of_people', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Field('description'),
        )
    
    class Meta:
        """Meta options for the form."""
        model = Booking
        fields = [
            'facility', 'title', 'description', 
            'start_time', 'end_time', 'number_of_people'
        ]
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        
        # If required fields are not present, don't proceed with validation
        if not all(field in cleaned_data for field in ['facility', 'start_time', 'end_time']):
            return cleaned_data
        
        # Set user if not already set (for new bookings)
        if not self.instance.pk and self.user:
            self.instance.user = self.user
        
        return cleaned_data


class BookingFilterForm(forms.Form):
    """Form for filtering bookings."""
    STATUS_CHOICES = (
        ('', _('All')),
        ('pending', _('Pending')),
        ('confirmed', _('Confirmed')),
        ('cancelled', _('Cancelled')),
    )
    
    facility = forms.ModelChoiceField(
        label=_('Facility'),
        queryset=Facility.objects.filter(is_active=True),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=STATUS_CHOICES,
        required=False
    )
    date_from = forms.DateField(
        label=_('From Date'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    date_to = forms.DateField(
        label=_('To Date'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Setup Crispy form layout
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Row(
                Column('facility', css_class='form-group col-md-6'),
                Column('status', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('date_from', css_class='form-group col-md-6'),
                Column('date_to', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Submit('submit', _('Filter'), css_class='btn btn-primary')
        )
    
    def filter_queryset(self, queryset):
        """Filter the queryset based on form data."""
        facility = self.cleaned_data.get('facility')
        status = self.cleaned_data.get('status')
        date_from = self.cleaned_data.get('date_from')
        date_to = self.cleaned_data.get('date_to')
        
        if facility:
            queryset = queryset.filter(facility=facility)
            
        if status:
            queryset = queryset.filter(status=status)
            
        if date_from:
            queryset = queryset.filter(start_time__date__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(start_time__date__lte=date_to)
            
        return queryset
