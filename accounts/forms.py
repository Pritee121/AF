
from django import forms
from .models import User
from django.core.validators import MinLengthValidator

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), validators=[MinLengthValidator(6)])
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_image', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")

        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())

class OTPForm(forms.Form):
    otp = forms.CharField(max_length=6)



from django import forms
from .models import User
from django.contrib.auth.hashers import make_password

class ProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_image', 'password']

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return make_password(password)  # Hash new password
        return None  # Return None if password field is empty



from django import forms
from .models import User

class ArtistRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'password', 'profile_image',
                  'city', 'works_at', 'experience_years', 'training_certificate']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match!")

        return cleaned_data



from django import forms
from .models import User

class ProfileUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city', 'works_at', 'experience_years', 'profile_image', 'password', 'training_certificate']



from django import forms
from .models import Work

class WorkUploadForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'description', 'image']




from django import forms
from .models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'price', 'available_date','duration', 'available_time', 'description']
        widgets = {
            'available_date': forms.DateInput(attrs={'type': 'date'}),
            'available_time': forms.TimeInput(attrs={'type': 'time'}),
        }