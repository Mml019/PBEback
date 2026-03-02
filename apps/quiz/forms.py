from django import forms
from django.contrib.auth.forms import AuthenticationForm
from apps.quiz.models import MyUser

class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, required=True)
    password = forms.CharField(max_length=20, required=True, widget=forms.PasswordInput)
       
    class Meta:
        model = MyUser,
        fields=["username", "password"]

