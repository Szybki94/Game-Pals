from django import forms


# MODELS
from .models import Group


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'created_by']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'}),
                   'created_by': forms.HiddenInput}
