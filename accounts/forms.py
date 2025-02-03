
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

# class ServiceForm(forms.ModelForm):
#     class Meta:
#         model = Service
#         fields = ['service_name', 'price', 'available_date','duration', 'available_time', 'description']
#         widgets = {
#             'available_date': forms.DateInput(attrs={'type': 'date'}),
#             'available_time': forms.TimeInput(attrs={'type': 'time'}),
#         }

### ✅ Service Form with Auto Duration Handling ###
from django import forms
from .models import Service
from django.core.exceptions import ValidationError
from datetime import date

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'price', 'available_date', 'duration', 'available_time', 'description']
        widgets = {
            'available_date': forms.DateInput(attrs={'type': 'date'}),
            'available_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_duration(self):
        """ Ensure that duration is not empty """
        duration = self.cleaned_data.get('duration')
        if not duration:
            raise ValidationError("Duration cannot be empty.")
        return duration

    def clean_available_date(self):
        """ Ensure that the available date is not in the past """
        available_date = self.cleaned_data.get('available_date')
        if available_date and available_date < date.today():
            raise ValidationError("Available date cannot be in the past.")
        return available_date


from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'date', 'time', 'payment_method']

    def clean(self):
        cleaned_data = super().clean()
        artist = cleaned_data.get("service").artist
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        # Prevent duplicate booking for same artist, date, and time
        if Booking.objects.filter(artist=artist, date=date, time=time).exists():
            raise forms.ValidationError("This time slot is already booked. Please select another.")

        return cleaned_data



from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your review...'})
        }
