from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from djgentelella.forms.forms import GTForm

from .models import Client, Account
from djgentelella.widgets import core as gentelella_widgets
from django.core.exceptions import ValidationError

class Client_Registration_Form(GTForm, UserCreationForm):

    name = forms.CharField(widget=gentelella_widgets.TextInput, label='Client name', help_text='Enter the name of the client, please.', max_length=100, required=True)
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

class Custom_Authentication_Form(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
        label='Password'
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not User.objects.filter(username=username).exists():
            raise ValidationError("Username does not exist.")
        return username

class Delete_Confirmation_Form(forms.Form):
    confirm = forms.BooleanField(required=True, label="Confirmar eliminación")

class Account_Form(forms.ModelForm, GTForm):
    class Meta:
        model = Account
        fields = ['client', 'bank_fund', 'card_pin']
        widgets = {
            'client': gentelella_widgets.Select(attrs={'class': 'form-control'}),
            'bank_fund': gentelella_widgets.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank fund amount'
            }),
            'card_pin': gentelella_widgets.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter 4-digit PIN'
            })
        }

class Edit_Account_Form(forms.ModelForm, GTForm):
    class Meta:
        model = Account
        fields = ['bank_fund', 'card_pin']
        widgets = {
            'bank_fund': gentelella_widgets.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter bank fund amount'
            }),
            'card_pin': gentelella_widgets.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter 4-digit PIN'
            })
        }

class Edit_Client_Form(forms.ModelForm, GTForm):

    username = forms.CharField(widget=gentelella_widgets.TextInput, max_length=150, required=True)
    name = forms.CharField(widget=gentelella_widgets.TextInput, max_length=255, required=True)

    class Meta:
        model = Client
        fields = ['name', 'username']

    def __init__(self, *args, **kwargs):
        super(Edit_Client_Form, self).__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['username'].initial = self.instance.user.username

    def save(self, commit=True):
        client = super(Edit_Client_Form, self).save(commit=False)
        if commit:
            client.save()
            client.user.username = self.cleaned_data['username']
            client.user.save()
        return client