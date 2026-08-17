from django import forms
from .models import Paiement

class PaiementAdminForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = '__all__'
