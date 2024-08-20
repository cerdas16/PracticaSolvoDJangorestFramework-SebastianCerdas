from django import forms
from djgentelella.widgets import PasswordInput

class LoginForm(forms.Form):
    password = forms.CharField(widget=PasswordInput())