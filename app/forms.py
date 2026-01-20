from django.forms import ModelForm, Form
from django.forms import CharField, PasswordInput


class UserLoginForm(Form):
    username = CharField(max_length=100)
    password = CharField(widget=PasswordInput)