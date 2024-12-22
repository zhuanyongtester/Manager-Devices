from datetime import datetime

from django import forms
from rest_framework.exceptions import ValidationError



class UserRegistrationForm(forms.Form):
    login_id = forms.CharField(max_length=128)
    password = forms.CharField(max_length=256, widget=forms.PasswordInput)
    name = forms.CharField(max_length=128)
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    birthday = forms.DateField()
    location = forms.CharField(max_length=256)
    age = forms.IntegerField(min_value=0)
    language = forms.CharField(max_length=128)
    login_type = forms.ChoiceField(choices=[('email', 'Email'), ('phone', 'Phone')])


    def clean_login_id(self):
        login_id = self.cleaned_data.get('login_id')
        if not login_id:
            raise ValidationError("login_id is required and cannot be empty")
        return login_id
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("password is required and cannot be empty")
        return password
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Name is required and cannot be empty")
        return name

    def clean_gender(self):
        gender = self.cleaned_data.get('gender')
        if gender not in ['male', 'female', 'other']:
            raise ValidationError("Please choose gender (male, female, or other)")
        return gender

    def clean_birthday(self):
        birthday = self.cleaned_data.get('birthday')
        if not self.validate_birthday(birthday):
            raise ValidationError("Invalid birthday format or date")
        return birthday

    def clean_location(self):
        location = self.cleaned_data.get('location')
        if not location.strip():
            raise ValidationError("Location is required and cannot be empty")
        return location

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 0:
            raise ValidationError("Age must be a positive integer")
        return age

    def clean_language(self):
        language = self.cleaned_data.get('language')
        if not language.strip():
            raise ValidationError("Language is required and cannot be empty")
        return language

    def clean_login_type(self):
        login_type = self.cleaned_data.get('login_type')
        if login_type not in ['email', 'phone']:
            raise ValidationError("Please choose login_type (email, phone)")
        return login_type


    def validate_birthday(self, birthday):
        try:
            birth_date = datetime.strptime(str(birthday), '%Y-%m-%d')
            return birth_date < datetime.now()  # 确保出生日期小于当前日期
        except ValueError:
            return False


    def clean(self):
        cleaned_data = super().clean()
        # 在此添加需要跨字段验证的逻辑
        return cleaned_data

class UserLoginForm(forms.Form):
    login_id = forms.CharField(max_length=128)
    password = forms.CharField(max_length=256, widget=forms.PasswordInput)
    login_type = forms.ChoiceField(choices=[('email', 'Email'), ('phone', 'Phone')])
    def clean_login_id(self):
        login_id = self.cleaned_data.get('login_id')
        if not login_id:
            raise ValidationError("login_id is required and cannot be empty")
        return login_id
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise ValidationError("password is required and cannot be empty")
        return password
    def clean_login_type(self):
        login_type = self.cleaned_data.get('login_type')
        if login_type not in ['email', 'phone']:
            raise ValidationError("Please choose login_type (email, phone)")
        return login_type

    def clean(self):
        cleaned_data = super().clean()
        # 在此添加需要跨字段验证的逻辑
        return cleaned_data