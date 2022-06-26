# DJANGO MODULES
from django import forms
from django.forms import ModelForm
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.models import User

# MODELS
from .models import Event
from Home.models import Game, UserGames


# UTILITIES


# FORMS

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


class EventDeleteForm(forms.Form):
    class Meta:
        model = Event
        fields = ['id']
        widgets = {'id': forms.HiddenInput()}
