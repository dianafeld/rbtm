from main.models import UserProfile
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserRegistrationForm(UserCreationForm):    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class UserProfileRegistrationForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'role')
