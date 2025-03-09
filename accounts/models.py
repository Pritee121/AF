from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.timezone import now


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None  
    email = models.EmailField(unique=True)  # Email as the unique identifier
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_artist = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)  #Admin approval
    otp = models.CharField(max_length=6, blank=True, null=True)  #Stores OTP
    
    works_at = models.CharField(max_length=255, null=True, blank=True)
    experience_years = models.IntegerField(default=0, null=True, blank=True)
    # training_certificate = models.FileField(upload_to="certificates/", null=True, blank=True)
    is_available = models.BooleanField(default=True) 
    

    USERNAME_FIELD = "email"  #Login using email instead of username
    REQUIRED_FIELDS = []  #Don't require username

    objects = CustomUserManager()  #Use custom manager

    

    def __str__(self):
        return self.email


class TrainingCertificate(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    certificate = models.FileField(upload_to="certificates/")

    def __str__(self):
        return f"Certificate for {self.artist.email}"


class Work(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)  #Reference the corrected User model
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='works/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.artist.first_name}"
    
# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class WorkingTime(models.Model):
#     artist = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # ✅ Set default user ID
#     day = models.CharField(max_length=10, choices=[
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     ], unique=True)
#     opening_time = models.TimeField()
#     closing_time = models.TimeField()

#     def __str__(self):
#         return f"{self.day}: {self.opening_time} to {self.closing_time}"
# from datetime import timedelta
# class Service(models.Model):
#     artist = models.ForeignKey(User, related_name="services", on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.DurationField()
#     travel_time = models.DurationField(default=timedelta(minutes=30))
#     total_duration = models.DurationField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     work_days = models.ManyToManyField(WorkingTime, blank=True, related_name="services")  # ✅ Correct Many-to-Many

#     def get_work_days(self):
#         """Fetch all working days for this service."""
#         return list(self.work_days.values_list("day", flat=True))

#     def save(self, *args, **kwargs):
#         if self.duration and self.travel_time:
#             self.total_duration = self.duration + self.travel_time
#         super().save(*args, **kwargs)

#     def get_total_duration_hms(self):
#         if self.total_duration:
#             seconds = int(self.total_duration.total_seconds())
#             hours, remainder = divmod(seconds, 3600)
#             minutes, seconds = divmod(remainder, 60)
#             return f"{hours:02}:{minutes:02}:{seconds:02}"
#         return "00:00:00"

#     def __str__(self):
#         return f"{self.service_name} ({self.get_total_duration_hms()}) - {self.artist.first_name}"
from django.db import models
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime

User = get_user_model()

class WorkingTime(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  
    day = models.CharField(max_length=10, choices=[
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ], unique=True)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return f"{self.day}: {self.opening_time} to {self.closing_time}"

# class Service(models.Model):
#     artist = models.ForeignKey(User, related_name="services", on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.DurationField()
#     travel_time = models.DurationField(default=timedelta(minutes=30))
#     total_duration = models.DurationField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     work_days = models.ManyToManyField(WorkingTime, blank=True, related_name="services")  

#     def save(self, *args, **kwargs):
#         if self.duration and self.travel_time:
#             self.total_duration = self.duration + self.travel_time
#         super().save(*args, **kwargs)

#     from datetime import datetime, timedelta

#     def generate_slots_for_day(self, work_day):
#         """Generate available time slots based on working hours and service duration."""
#         slots = []
#         opening = datetime.combine(datetime.today(), work_day.opening_time)
#         closing = datetime.combine(datetime.today(), work_day.closing_time)
#         current_time = opening

#         # ✅ Ensure total_duration is not None
#         if self.total_duration is None:
#             print(f"⚠️ Warning: Service {self.service_name} has no total duration set!")
#             return slots  # Return empty list to avoid errors

#         while current_time + self.total_duration <= closing:
#             next_slot = current_time + self.total_duration
#             slots.append(f"{current_time.strftime('%H:%M')} - {next_slot.strftime('%H:%M')}")
#             current_time = next_slot  # Move to the next slot

#         return slots

#     def get_total_duration_hms(self):
#         """Convert total duration to HH:MM:SS format"""
#         if self.total_duration:
#             seconds = int(self.total_duration.total_seconds())
#             hours, remainder = divmod(seconds, 3600)
#             minutes, seconds = divmod(remainder, 60)
#             return f"{hours:02}:{minutes:02}:{seconds:02}"
#         return "00:00:00"
#     def __str__(self):
#         return f"{self.service_name} ({self.total_duration}) - {self.artist.first_name}"
from datetime import datetime, timedelta

class Service(models.Model):
    artist = models.ForeignKey(User, related_name="services", on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.DurationField()
    travel_time = models.DurationField(default=timedelta(minutes=30))
    total_duration = models.DurationField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    work_days = models.ManyToManyField(WorkingTime, blank=True, related_name="services")  

    def save(self, *args, **kwargs):
        """Ensure total duration is calculated before saving"""
        if self.duration and self.travel_time:
            self.total_duration = self.duration + self.travel_time
        super().save(*args, **kwargs)

    def generate_slots_for_day(self, work_day):
        """Generate available time slots dynamically based on working hours and service duration."""
        slots = []
        
        if self.total_duration is None:
            print(f"⚠️ Warning: Service {self.service_name} has no total duration set!")
            return slots  # Return empty list to avoid errors

        # Convert working time into datetime format
        opening_time = datetime.combine(datetime.today(), work_day.opening_time)
        closing_time = datetime.combine(datetime.today(), work_day.closing_time)
        current_time = opening_time

        while current_time + self.total_duration <= closing_time:
            next_slot = current_time + self.total_duration
            slots.append(f"{current_time.strftime('%H:%M')} - {next_slot.strftime('%H:%M')}")
            current_time = next_slot  # Move to the next slot

        return slots

    def get_working_days(self):
        """Fetch all working days for this service."""
        return list(self.work_days.values_list("day", flat=True))

    def get_slots_json(self):
        """Return available slots for each working day in JSON format."""
        slots_data = {}
        for work_day in self.work_days.all():
            slots_data[work_day.day] = self.generate_slots_for_day(work_day)
        return slots_data

    def get_total_duration_hms(self):
        """Convert total duration to HH:MM:SS format"""
        if self.total_duration:
            seconds = int(self.total_duration.total_seconds())
            hours, remainder = divmod(seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02}:{minutes:02}:{seconds:02}"
        return "00:00:00"

    def __str__(self):
        return f"{self.service_name} ({self.get_total_duration_hms()}) - {self.artist.first_name}"

# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class Service(models.Model):
#     artist = models.ForeignKey(User, related_name='services', on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.CharField(max_length=50, default="30 mins")
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.service_name} ({self.duration}) - {self.artist.first_name}"

# from django.db import models
# from django.contrib.auth import get_user_model
# from multiselectfield import MultiSelectField

# User = get_user_model()

# class Service(models.Model):
#     artist = models.ForeignKey(User, related_name='services', on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.IntegerField()
#     travel_time = models.IntegerField()
#     total_duration = models.IntegerField(blank=True, null=True)  # Auto-calculated
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     WEEKDAYS = [
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     ]

#     work_days = MultiSelectField(choices=WEEKDAYS, max_length=100, blank=True, default=['Monday'])

#     def __str__(self):
#         return f"{self.service_name} ({self.price} Rs.) - {self.artist.first_name}"
from datetime import timedelta

#     def save(self, *args, **kwargs):
#         self.total_duration = self.duration + self.travel_time
#         super().save(*args, **kwargs)
from django.db import models
from multiselectfield import MultiSelectField

# from django.contrib.auth import get_user_model
# from multiselectfield import MultiSelectField
# from datetime import timedelta

# User = get_user_model()

# class Service(models.Model):
#     artist = models.ForeignKey(User, related_name='services', on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
    
#     duration = models.DurationField()  # ✅ Store duration as time (hours & minutes)
#     travel_time = models.DurationField()  # ✅ Store travel time as time (hours & minutes)
#     total_duration = models.DurationField(blank=True, null=True)  # Auto-calculated
    
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     WEEKDAYS = [
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     ]

#     work_days = MultiSelectField(choices=WEEKDAYS, max_length=100, blank=True, default=['Monday'])

#     def save(self, *args, **kwargs):
#         if self.duration and self.travel_time:
#             self.total_duration = self.duration + self.travel_time  # ✅ Auto-calculate total duration
#         super().save(*args, **kwargs)

#     def get_duration_display(self):
#         """ ✅ Convert timedelta to a human-readable format (hours & minutes) """
#         hours, remainder = divmod(self.duration.total_seconds(), 3600)
#         minutes, _ = divmod(remainder, 60)
#         return f"{int(hours)}h {int(minutes)}m"

#     def get_travel_time_display(self):
#         """ ✅ Convert timedelta to a human-readable format """
#         hours, remainder = divmod(self.travel_time.total_seconds(), 3600)
#         minutes, _ = divmod(remainder, 60)
#         return f"{int(hours)}h {int(minutes)}m"

#     def get_total_duration_display(self):
#         """ ✅ Convert total_duration timedelta to a readable format """
#         if self.total_duration:
#             hours, remainder = divmod(self.total_duration.total_seconds(), 3600)
#             minutes, _ = divmod(remainder, 60)
#             return f"{int(hours)}h {int(minutes)}m"
#         return "N/A"

#     def __str__(self):
#         return f"{self.service_name} ({self.get_duration_display()}) - {self.artist.first_name}"
# from django.db import models
# from django.contrib.auth import get_user_model
# from datetime import timedelta, datetime
# from multiselectfield import MultiSelectField

# User = get_user_model()

# from datetime import timedelta

# class Service(models.Model):
#     artist = models.ForeignKey(User, related_name='services', on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.DurationField()
#     travel_time = models.DurationField(default=timedelta(minutes=30))  # Set a default value
#     total_duration = models.DurationField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)


#     WEEKDAYS = [
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     ]

#     work_days = MultiSelectField(choices=WEEKDAYS, max_length=100, blank=True, default=['Monday'])

#     def save(self, *args, **kwargs):
#         if self.duration and self.travel_time:
#             self.total_duration = self.duration + self.travel_time
#         super().save(*args, **kwargs)


# class Service(models.Model):
#     artist = models.ForeignKey(User, related_name='services', on_delete=models.CASCADE)
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.DurationField()
#     travel_time = models.DurationField(default=timedelta(minutes=30))
#     total_duration = models.DurationField(blank=True, null=True)
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     WEEKDAYS = [
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     ]

#     work_days = MultiSelectField(choices=WEEKDAYS, max_length=100, blank=True, default=['Monday'])

#     def save(self, *args, **kwargs):
#         if self.duration and self.travel_time:
#             self.total_duration = self.duration + self.travel_time
#         super().save(*args, **kwargs)

#     def get_total_duration_hms(self):
#         """Returns duration in HH:MM:SS format"""
#         if self.total_duration:
#             seconds = int(self.total_duration.total_seconds())
#             hours, remainder = divmod(seconds, 3600)
#             minutes, seconds = divmod(remainder, 60)
#             return f"{hours:02}:{minutes:02}:{seconds:02}"  # Ensure two-digit format
#         return "00:00:00"

# class ServiceSchedule(models.Model):
#     service = models.ForeignKey(Service, related_name='schedules', on_delete=models.CASCADE)
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     weekday = models.CharField(max_length=10, choices=Service.WEEKDAYS, default='Monday')  # ✅ Default to Monday

#     class Meta:
#         unique_together = ('service', 'weekday', 'start_time')
# class ServiceSchedule(models.Model):
#     service = models.ForeignKey(Service, related_name='schedules', on_delete=models.CASCADE)
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     weekday = models.CharField(max_length=10, choices=Service.WEEKDAYS, default='Monday')  # Default to Monday

#     class Meta:
#         unique_together = ('service', 'weekday', 'start_time')


#     def __str__(self):
#         return f"{self.service.service_name} - {self.weekday} {self.start_time} - {self.end_time}"

# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class Booking(models.Model):
#     PAYMENT_CHOICES = [
#         ("khalti", "Khalti"),
#         ("cod", "Cash on Delivery"),
#     ]
#     STATUS_CHOICES = [
#         ("Pending", "Pending"),
#         ("Confirmed", "Confirmed"),
#         ("Cancelled", "Cancelled"),
#     ]
    
#     artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
#     client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_bookings")
#     service = models.ForeignKey("Service", on_delete=models.CASCADE, null=True, blank=True)
#     date = models.DateField()
#     time = models.TimeField()
#     payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
#     payment_status = models.CharField(max_length=20, default="Pending")
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Allow 6 decimal places
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Allow 6 decimal places
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('artist', 'date', 'time')  # Prevent duplicate bookings

#     def __str__(self):
#         return f"{self.client.first_name} booked {self.artist.first_name} for {self.service.service_name} on {self.date} using {self.payment_method}"
# from django.db import models
# from django.contrib.auth import get_user_model
# from datetime import timedelta

# User = get_user_model()

# class Booking(models.Model):
#     PAYMENT_CHOICES = [
#         ("khalti", "Khalti"),
#         ("cod", "Cash on Delivery"),
#     ]
#     STATUS_CHOICES = [
#         ("Pending", "Pending"),
#         ("Confirmed", "Confirmed"),
#         ("Cancelled", "Cancelled"),
#     ]
    
#     artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
#     client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_bookings")
#     service = models.ForeignKey("Service", on_delete=models.CASCADE, null=True, blank=True)
    
#     date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField(null=True, blank=True)  # Auto-calculated
    
#     payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
#     payment_status = models.CharField(max_length=20, default="Pending")
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('artist', 'date', 'start_time', 'end_time')  # Prevent overlapping bookings

#     def calculate_end_time(self):
#         """Calculate and update end_time based on service duration."""
#         if self.service and self.start_time:
#             start_datetime = datetime.combine(self.date, self.start_time)
#             end_datetime = start_datetime + timedelta(minutes=self.service.duration)
#             self.end_time = end_datetime.time()

#     def save(self, *args, **kwargs):
#         """Auto-calculate end_time before saving the model."""
#         if not self.end_time:
#             self.calculate_end_time()
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return (f"{self.client.first_name} booked {self.artist.first_name} for "
#                 f"{self.service.service_name} on {self.date} from {self.start_time} to {self.end_time} "
#                 f"using {self.payment_method}")
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

User = get_user_model()

class Booking(models.Model):
    PAYMENT_CHOICES = [
        ("khalti", "Khalti"),
        ("cod", "Cash on Delivery"),
    ]
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
    ]
    
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_bookings")
    service = models.ForeignKey("Service", on_delete=models.CASCADE, null=True, blank=True)
    
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(null=True, blank=True)  # ✅ Ensure end_time can be saved
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
    payment_status = models.CharField(max_length=20, default="Pending")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('artist', 'date', 'start_time', 'end_time')  # Prevent overlapping bookings
    def mark_completed(self):
        """ ✅ Marks booking as completed """
        self.status = "Completed"
        self.save()
    def calculate_end_time(self):
        """✅ Ensure end_time is calculated correctly."""
        if self.service and self.start_time:
            start_datetime = datetime.combine(self.date, self.start_time)
            total_minutes = int(self.service.duration.total_seconds() / 60) + int(self.service.travel_time.total_seconds() / 60)
            end_datetime = start_datetime + timedelta(minutes=total_minutes)
            self.end_time = end_datetime.time()

    def clean(self):
        """✅ Prevent overlapping bookings before saving."""
        overlapping_bookings = Booking.objects.filter(
            artist=self.artist,
            date=self.date
        ).filter(
            Q(start_time__lt=self.end_time, end_time__gt=self.start_time)  # Check for overlapping bookings
        )

        if self.pk:
            overlapping_bookings = overlapping_bookings.exclude(pk=self.pk)  # Exclude self in case of update

        if overlapping_bookings.exists():
            raise ValidationError("This time slot is already booked. Please choose a different time.")

    def save(self, *args, **kwargs):
        """✅ Ensure end_time is set before saving and check for conflicts."""
        if not self.end_time:
            self.calculate_end_time()
        self.clean()  # ✅ Check for conflicts before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return (f"{self.client.first_name} booked {self.artist.first_name} for "
                f"{self.service.service_name} on {self.date} from {self.start_time} to {self.end_time} "
                f"using {self.payment_method}")


class ServiceAvailability(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="availability")
    available_date = models.DateField()
    start_time = models.TimeField(default='00:00:00')  # Default time (midnight)
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('service', 'available_date', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.service} - {self.available_date} {self.start_time} - {'Booked' if self.is_booked else 'Available'}"

    def mark_as_booked(self):
        """ Mark the slot as booked when a new booking is created """
        self.is_booked = True
        self.save()

    def mark_as_available(self):
        """ Mark the slot as available again when a booking is cancelled """
        self.is_booked = False
        self.save()


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.client.first_name}: {self.message}"

from django.db import models


class AboutUs(models.Model):
    title = models.CharField(max_length=255, default="About Us")
    content = models.TextField()  # stores the about us content

    def __str__(self):
        return self.title  # Display title in admin panel

from django.db import models


class ContactUsPage(models.Model):
    title = models.CharField(max_length=255, default="Contact Us")
    content = models.TextField()  # Editable contact page content from admin
    email = models.EmailField()  # Admin email for contact

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

class Review(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artist_reviews")  # Link to artist
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_reviews", null=True, blank=True)  # Allow NULL
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    is_anonymous = models.BooleanField(default=False)  # New: Anonymous Option
    created_at = models.DateTimeField(auto_now_add=True)
    artist_reply = models.TextField(blank=True, null=True)  # Artist reply field


    def __str__(self):
        return f"{self.user.first_name} reviewed {self.artist.first_name} - {self.rating} Stars"


from django.contrib.auth import get_user_model
from django.db import models
from multiselectfield import MultiSelectField  # Import MultiSelectField

User = get_user_model()

class WeekSchedule(models.Model):
    WEEKDAYS = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    weekdays = MultiSelectField(choices=WEEKDAYS, max_length=100, default='Monday')  # ✅ Set default to Monday
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.artist.email} - {self.weekdays}: {self.start_time} to {self.end_time}"







# class ServiceSchedule(models.Model):
#     service = models.ForeignKey(Service, related_name='schedules', on_delete=models.CASCADE)
#     start_time = models.TimeField()
#     end_time = models.TimeField()

#     def __str__(self):
#         return f"{self.service.service_name}: {self.start_time} - {self.end_time}"


# from django.db import models


# class WorkingTime(models.Model):
#     DAY_CHOICES = [
#         ('Monday', 'Monday'),
#         ('Tuesday', 'Tuesday'),
#         ('Wednesday', 'Wednesday'),
#         ('Thursday', 'Thursday'),
#         ('Friday', 'Friday'),
#         ('Saturday', 'Saturday'),
#         ('Sunday', 'Sunday'),
#     ]
    
#     day = models.CharField(max_length=10, choices=DAY_CHOICES, unique=True)
#     opening_time = models.TimeField()
#     closing_time = models.TimeField()

#     def __str__(self):
#         return f"{self.day}: {self.opening_time} - {self.closing_time}"






