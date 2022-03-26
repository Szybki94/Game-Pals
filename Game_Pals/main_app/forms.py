from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        widgets = {
            'password': forms.PasswordInput(render_value=True, attrs={'class': "form-control"}),
            'username': forms.TextInput(attrs={'class': "form-control"})
        }
        fields = ['username', 'password']
