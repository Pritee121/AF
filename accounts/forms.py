from django import forms
from .models import User
from django.core.validators import MinLengthValidator

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), validators=[MinLengthValidator(6)])
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone','city', 'profile_image', 'password']

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
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_image','city', 'password']

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
                  'works_at', 'experience_years', 'profile_image']

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
from .models import TrainingCertificate

class TrainingCertificateForm(forms.ModelForm):
    class Meta:
        model = TrainingCertificate
        fields = ["certificate"]

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

# class ServiceForm(forms.ModelForm):
#     class Meta:
#         model = Service
#         fields = ['service_name', 'price', 'duration', 'description']
# from django import forms
# from .models import Service

# class ServiceForm(forms.ModelForm):
#     class Meta:
#         model = Service
#         fields = ['service_name', 'price', 'duration', 'travel_time', 'description', 'work_days']
#         widgets = {
#             'service_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter service name'}),
#             'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter price'}),
#             'duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
#             'travel_time': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
#             'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
#             'work_days': forms.CheckboxSelectMultiple(),
#         }
from django import forms
from .models import Service
from datetime import timedelta

class ServiceForm(forms.ModelForm):
    duration_hours = forms.IntegerField(
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        label="Duration (Hours)"
    )
    duration_minutes = forms.IntegerField(
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 59}),
        label="Duration (Minutes)"
    )
    travel_time_hours = forms.IntegerField(
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        label="Travel Time (Hours)"
    )
    travel_time_minutes = forms.IntegerField(
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 59}),
        label="Travel Time (Minutes)"
    )

    class Meta:
        model = Service
        fields = ['service_name', 'price', 'description', 'work_days']

    def clean(self):
        cleaned_data = super().clean()
        duration_hours = cleaned_data.get("duration_hours", 0)
        duration_minutes = cleaned_data.get("duration_minutes", 0)
        travel_time_hours = cleaned_data.get("travel_time_hours", 0)
        travel_time_minutes = cleaned_data.get("travel_time_minutes", 0)

        cleaned_data['duration'] = timedelta(hours=duration_hours, minutes=duration_minutes)
        cleaned_data['travel_time'] = timedelta(hours=travel_time_hours, minutes=travel_time_minutes)
        
        return cleaned_data

    def save(self, commit=True):
        service = super().save(commit=False)
        service.duration = timedelta(
            hours=self.cleaned_data["duration_hours"], 
            minutes=self.cleaned_data["duration_minutes"]
        )
        service.travel_time = timedelta(
            hours=self.cleaned_data["travel_time_hours"], 
            minutes=self.cleaned_data["travel_time_minutes"]
        )
        if commit:
            service.save()
        return service


from django import forms
from .models import ServiceAvailability

class ServiceAvailabilityForm(forms.ModelForm):
    class Meta:
        model = ServiceAvailability
        fields = ['available_date', 'start_time', 'end_time']



# from django import forms
# from .models import Booking

# class BookingForm(forms.ModelForm):
#     latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
#     longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

#     class Meta:
#         model = Booking
#         fields = ['service', 'date', 'time', 'payment_method', 'latitude', 'longitude']

#     def clean(self):
#         cleaned_data = super().clean()
#         artist = cleaned_data.get("service").artist
#         date = cleaned_data.get("date")
#         time = cleaned_data.get("time")

#         # Prevent duplicate booking for same artist, date, and time
#         if Booking.objects.filter(artist=artist, date=date, time=time).exists():
#             raise forms.ValidationError("This time slot is already booked. Please select another.")

#         return cleaned_data
from django import forms
from .models import Booking
from datetime import datetime, timedelta

class BookingForm(forms.ModelForm):
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Booking
        fields = ['service', 'date', 'start_time', 'payment_method', 'latitude', 'longitude']

    def clean(self):
        cleaned_data = super().clean()
        service = cleaned_data.get("service")
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")

        if not service or not date or not start_time:
            raise forms.ValidationError("All fields are required.")

        artist = service.artist
        service_duration = service.duration  # Duration in minutes

        # Calculate `end_time` based on service duration
        end_time = (datetime.combine(datetime.today(), start_time) + timedelta(minutes=service_duration)).time()

        # Prevent overlapping bookings
        overlapping_booking = Booking.objects.filter(
            artist=artist,
            date=date,
            start_time__lte=end_time,  # Prevents start time conflicts
            end_time__gte=start_time   # Prevents end time conflicts
        ).exists()

        if overlapping_booking:
            raise forms.ValidationError("This time slot is already booked. Please select another.")

        # Store calculated `end_time` in cleaned data (used in views)
        cleaned_data["end_time"] = end_time

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

from django import forms
from .models import Review

class ReviewReplyForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["artist_reply"]
        widgets = {
            "artist_reply": forms.Textarea(attrs={"rows": 2, "placeholder": "Write a reply..."}),
        }
from django import forms
from .models import WeekSchedule

class WeekScheduleForm(forms.ModelForm):
    class Meta:
        model = WeekSchedule
        fields = ['weekdays', 'start_time', 'end_time']
        widgets = {
            'weekdays': forms.CheckboxSelectMultiple(),  # Show checkboxes for weekdays
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
from django import forms
from .models import ServiceSchedule, Service

# class ServiceScheduleForm(forms.ModelForm):
#     service = forms.ModelChoiceField(
#         queryset=Service.objects.all(),
#         widget=forms.Select(attrs={'class': 'form-control'})
#     )
#     start_time = forms.TimeField(
#         widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
#     )

#     class Meta:
#         model = ServiceSchedule
#         fields = ['service', 'start_time']

from django import forms
from .models import ServiceSchedule

from django import forms
from .models import ServiceSchedule

class ServiceScheduleForm(forms.ModelForm):
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = ServiceSchedule
        fields = ['service', 'start_time']
from django import forms
from .models import WorkingTime

class WorkingTimeForm(forms.ModelForm):
    class Meta:
        model = WorkingTime
        fields = ['day', 'opening_time', 'closing_time']
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }
