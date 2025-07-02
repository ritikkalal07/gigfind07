# forms.py
from django import forms
from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from .models import Admin_register

class AdminRegisterForm(forms.ModelForm):
    password_confirm = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")

    class Meta:
        model = Admin_register
        fields = ['uname', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Admin_register.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class AdminLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        try:
            user = Admin_register.objects.get(email=email)
        except Admin_register.DoesNotExist:
            raise ValidationError("Email or password is incorrect.")

        if not check_password(password, user.password):
            raise ValidationError("Email or password is incorrect.")

        return cleaned_data
