from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client
from djgentelella.widgets import core as gentelella_widgets

class Client_Registration_Form(UserCreationForm):

    name = forms.CharField(widget=gentelella_widgets.TextInput, label='Enter the name of the client, please.' , max_length=100, required=True)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        client_name = Client(user=user,  name=self.cleaned_data['name'])
        if commit:
            client_name.save()
        return user
