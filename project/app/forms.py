from django import forms
from .models import Donor
class DonorCoordinates(forms.ModelForm):
    class Meta:
        fields = ['latitude','longitude']
        model = Donor