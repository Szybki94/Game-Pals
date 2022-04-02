from django import forms
from .models import Game
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
            "password1": forms.PasswordInput(render_value=True),
            "password2": forms.PasswordInput(render_value=True)
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


class UserUpdateForm1(forms.Form):
    games = forms.MultipleChoiceField(label="Games", widget=forms.CheckboxSelectMultiple)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        choices = tuple([
            (game.id, f'{game.name}')
            for game in Game.objects.all().order_by('name')
        ])

        self.fields['games'].choices = choices

# class Pizza2Form(forms.Form):
#     size = forms.ChoiceField(label="Wielkość", choices=PIZZA_SIZES, widget=forms.Select)
#     toppings = forms.MultipleChoiceField(label="Dodatki", widget=forms.CheckboxSelectMultiple)
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         choices = tuple( [ # Lista składana
#             (topping.id, f'{topping.name} ({topping.price})') # Element to krotka z id i opisem
#             for topping in Toppings.objects.all()
#         ] )
#         self.fields['toppings'].choices = choices
