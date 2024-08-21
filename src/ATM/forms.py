from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Client, Account
from djgentelella.widgets import core as gentelella_widgets
from django.core.exceptions import ValidationError

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

class Account_Form(forms.ModelForm):
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