from django import forms
from django.forms import DateTimeInput

class DateRangeForm(forms.Form):
    start_timestamp = forms.DateTimeField(label='start_timestamp', widget=DateTimeInput(attrs={'type': 'datetime-local'}))
    end_timestamp = forms.DateTimeField(label='end_timestamp', widget=DateTimeInput(attrs={'type': 'datetime-local'}))
