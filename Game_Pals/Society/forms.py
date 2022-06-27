# DJANGO MODULES
from django import forms
from django.contrib.auth.models import User

# MODELS
from Home.models import Friendship

# UTILITIES


# FORMS

class SendFriendInvitationForm(forms.Form):
    class Meta:
        model = Friendship
        fields = ['sender', 'receiver']
