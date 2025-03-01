"""
Forms for the facilities app.
"""
from django import forms
from django.utils.translation import gettext_lazy as _

from booking.apps.facilities.models import Facility


class FacilityFilterForm(forms.Form):
    """Form for filtering facilities."""
    name = forms.CharField(
        label=_('Name'), 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Search by name')})
    )
    location = forms.CharField(
        label=_('Location'), 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('Search by location')})
    )
    min_capacity = forms.IntegerField(
        label=_('Minimum Capacity'), 
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={'placeholder': _('Min capacity')})
    )
    
    def filter_queryset(self, queryset):
        """Filter the queryset based on form data."""
        name = self.cleaned_data.get('name')
        location = self.cleaned_data.get('location')
        min_capacity = self.cleaned_data.get('min_capacity')
        
        if name:
            queryset = queryset.filter(name__icontains=name)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if min_capacity:
            queryset = queryset.filter(capacity__gte=min_capacity)
            
        return queryset


class FacilityForm(forms.ModelForm):
    """Form for creating and updating facilities."""
    
    class Meta:
        """Meta options for the form."""
        model = Facility
        fields = [
            'name', 'location', 'capacity', 'description', 
            'image', 'is_active', 'opening_time', 'closing_time'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }
