from django import forms
from .models import Bitacora

class LogsForm(forms.ModelForm):
    class Meta:
        model = Bitacora
        fields = ['title', 'event', 'description', 'photo']
        widgets = {
            'title':forms.TextInput(attrs={'class':'form-control','placeholder':'Ingrese un título'}),
            'event':forms.Select(attrs={'class':'form-control'}),
            'description':forms.Textarea(attrs={'class':'form-control','placeholder':'Ingrese una descripción'}),
            'photo':forms.ClearableFileInput(attrs={'class':'form-control'}),
            }