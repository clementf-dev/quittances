from django import forms
from .models import Quittance
from datetime import date
from .models import Document

class GenererQuittanceForm(forms.Form):
    locataire_id = forms.IntegerField(widget=forms.HiddenInput)

    MOIS_CHOICES = Quittance.MOIS_CHOICES
    mois = forms.ChoiceField(choices=MOIS_CHOICES, label="Mois")
    annee = forms.IntegerField(
        initial=date.today().year,
        label="Année",
        min_value=2000,
        max_value=date.today().year
    )

class UploadDocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['fichier', 'description']