# django modules
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms import ModelForm, DateInput

# models
from .models import Game, UserGames, Profile, Event, Invitation
# utilities
from PIL import Image


class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "password": forms.PasswordInput(render_value=True, attrs={'class': "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        user = User.objects.filter(username=username).first()
        if user:
            self.add_error("password", "Wrong password")
            self.add_error("username", "Username looks correct ;)")
        return cleaned_data


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

        if "@" not in email:
            self.add_error("email", "Wrong email.")

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


class UserUpdateForm2(forms.Form):
    avatar = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    personal_info = forms.CharField(widget=forms.Textarea)

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.avatar.path)

        if img.height > 150 or img.width > 150:
            new_img = (150, 150)
            img.thumbnail(new_img)
            img.save(self.avatar.path)


class UserAddEventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'start_time']
        widgets = {"start_time": forms.DateTimeInput(format='%Y-%m-%dT%H:%M',
                                                     attrs={'class': 'form-control datetimepicker-input',
                                                            'data-target': '#datetimepicker1'}),
                   "name": forms.TextInput(attrs={"class": "form-control"}),
                   "description": forms.Textarea(attrs={"class": "form-control"})
                   }


class UserGameDeleteForm(forms.Form):
    class Meta:
        model = UserGames
        fields = ['id']


class SendFriendInvitationForm(forms.Form):
    class Meta:
        model = Invitation
        fields = ['sender', 'receiver']
