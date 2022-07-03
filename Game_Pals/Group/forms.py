from django import forms


# MODELS
from .models import Group, Comment


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'created_by']
        widgets = {'name': forms.TextInput(attrs={'class': 'form-control'}),
                   'created_by': forms.HiddenInput}


class GroupCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': "Leave your comment:"
        }
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control'})
                    }
