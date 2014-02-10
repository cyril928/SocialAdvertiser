import re

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from app_auth.models import UserProfile

# Global attributes

attrs_dict = { 'class': 'required' }

ROLE_CHOICES = (
    ('merchant', 'Merchant'),
    ('distributor', 'Ad Distributor'),
)

# Form class definitions

class SignupForm(forms.Form):
    role = forms.ChoiceField(choices=ROLE_CHOICES, label=_('Choose your role'))
    username = forms.RegexField(regex=r'^\w+$', max_length=30, widget=forms.TextInput(attrs=attrs_dict), label=_('Username'))
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=attrs_dict), label=_('First name'))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs=attrs_dict), label=_('Last name'))
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict, maxlength=75)), label=_('E-mail address'))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label=_('Password'))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False), label=_('Password (again)'))
    
    def clean_username(self):
        data = self.cleaned_data
        try:
            user = User.objects.get(username__iexact = data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_('This username is already taken. Please choose another.'))
        
    def clean(self):
        data = self.cleaned_data
        if 'password1' in data and 'password2' in data and data['password1'] != data['password2']:
            raise forms.ValidationError(_('Your passwords does not match. Please try again.'))
        return data

    def save(self):
        data = self.cleaned_data
        new_profile = UserProfile.objects.create_inactive_user(
            role=data['role'],
            username=data['username'], 
            first_name=data['first_name'], 
            last_name=data['last_name'], 
            email=data['email'], 
            password=data['password1'])
        return new_profile
        

class SigninForm(forms.Form):
    username = forms.RegexField(regex=r'^\w+$', max_length=30, widget=forms.TextInput(attrs=attrs_dict))
    password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False))
        
    def clean(self):
        data = self.cleaned_data
        username = data['username']
        password = data['password']  
        return data
