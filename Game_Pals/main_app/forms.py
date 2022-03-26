from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(render_value=True, attrs={'class': "form-control"}),
        }


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name", "username", "email", "password1", "password2"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.TextInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(render_value=True, attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(render_value=True, attrs={"class": "form-control"})
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get("username")
        email = cleaned_data.get("email")
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        user = User.objects.filter(username=username).first()
        if user:
            self.add_error("username", "User already exists.")

        # if "@" not in email:
        #     self.add_error("email", "Wrong email.")

        if password1 != password2:
            self.add_error("password2", "Passwords do not match.")

        return cleaned_data
