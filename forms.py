# filepath: d:\New folder\three_step_auth\forms.py
from django import forms

class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    step1 = forms.CharField(max_length=255, required=False)
    step2 = forms.CharField(max_length=255, required=False)
    step3 = forms.CharField(max_length=255, required=False)