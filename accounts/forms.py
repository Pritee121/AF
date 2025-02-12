
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
from django.core.exceptions import ValidationError

class ArtistRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Password", min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")
    profile_image = forms.ImageField(required=False, label="Upload Profile Image")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'city',
                  'works_at', 'experience_years', 'training_certificate', 'profile_image']

    def clean_confirm_password(self):
        """ ✅ Ensure passwords match """
        password = self.cleaned_data.get("password")
        confirm_password = self.cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match!")
        
        return confirm_password  # ✅ Ensure correct indentation

    def clean_profile_image(self):
        """ ✅ Validate profile image format """
        image = self.cleaned_data.get("profile_image")

        if image:
            allowed_formats = ["image/jpeg", "image/png", "image/jpg"]
            if image.content_type not in allowed_formats:
                raise ValidationError("Only JPEG and PNG images are allowed.")
        
        return image  # ✅ Ensure correct indentation






from django import forms
from .models import Work

class WorkUploadForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'description', 'image']



from django import forms
from .models import Service, ServiceAvailability
from django.forms import inlineformset_factory
from datetime import date
from django.core.exceptions import ValidationError

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'price', 'duration', 'description']

class ServiceAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ServiceAvailability
        fields = ['available_date', 'available_time']
        widgets = {
            'available_date': forms.DateInput(attrs={'type': 'date'}),
            'available_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean_available_date(self):
        """ Ensure available date is not in the past """
        available_date = self.cleaned_data.get('available_date')
        if available_date and available_date < date.today():
            raise ValidationError("Available date cannot be in the past.")
        return available_date

# ✅ Create Formset for Multiple Date & Time
ServiceAvailabilityFormSet = inlineformset_factory(
    Service, ServiceAvailability, form=ServiceAvailabilityForm,
    extra=1, can_delete=True
)


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




