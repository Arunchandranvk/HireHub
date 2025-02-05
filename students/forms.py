from django import forms
from college_admin.models import *

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['std_id']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['std_id','password']

from django.contrib.auth.forms import PasswordChangeForm


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Old Password"}), label="Old Password"
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "New Password"}),
        label="New Password"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Confirm New Password"}),
        label="Confirm New Password"
    )