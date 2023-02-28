from django import forms
from .models import Users


class ImageForm(forms.ModelForm):
    """Form for the image model"""
    class Meta:
        model = Users
        fields = ("first_name", "last_name", "email", "password", "user_image")
        labels = {
            "first_name": "",
            "last_name": "",
            "email": "",
            "password": "",
            "user_image": ""
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"placeholder": "Enter First Name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Enter Last Name"}),
            "email": forms.TextInput(attrs={"placeholder": "Enter Email"}),
            "password": forms.TextInput(attrs={"placeholder": "Enter Password"})
        }