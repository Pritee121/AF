



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
    username = None  # ✅ Remove username field completely
    email = models.EmailField(unique=True)  # Email as the unique identifier
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_artist = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)  # ✅ Stores OTP
    city = models.CharField(max_length=100, null=True, blank=True)
    works_at = models.CharField(max_length=255, null=True, blank=True)
    experience_years = models.IntegerField(default=0, null=True, blank=True)
    training_certificate = models.FileField(upload_to="certificates/", null=True, blank=True)
    is_available = models.BooleanField(default=True) 
    

    USERNAME_FIELD = "email"  # ✅ Login using email instead of username
    REQUIRED_FIELDS = []  # ✅ Don't require username

    objects = CustomUserManager()  # ✅ Use custom manager

    def __str__(self):
        return self.email







class Work(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ Reference the corrected User model
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='works/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.artist.first_name}"












# from django.db import models
# from django.contrib.auth import get_user_model

# User = get_user_model()


# class Service(models.Model):
#     artist = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to artist
#     service_name = models.CharField(max_length=255)
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     duration = models.CharField(max_length=50, default="30 mins")  # ✅ Added duration field
#     description = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.service_name} ({self.duration}) - {self.artist.first_name}"
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Service(models.Model):
    artist = models.ForeignKey(User, related_name='services', on_delete=models.CASCADE)
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=50, default="30 mins")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_name} ({self.duration}) - {self.artist.first_name}"

# from django.db import models

# class ServiceAvailability(models.Model):
#     service = models.ForeignKey("Service", on_delete=models.CASCADE)
#     available_date = models.DateField()
#     available_time = models.TimeField()
#     is_booked = models.BooleanField(default=False)  # ✅ Ensure this field exists

#     def __str__(self):
#         return f"{self.service} - {self.available_date} {self.available_time} - {'Booked' if self.is_booked else 'Available'}"


#     class Meta:
#         unique_together = ('service', 'available_date', 'available_time')  # Prevent duplicate entries

#     def __str__(self):
#         return f"{self.service.service_name} - {self.available_date} at {self.available_time}"







    


    
# from django.core.exceptions import ValidationError

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
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
#     # date = models.DateField()
#     date = models.DateTimeField(default=now, blank=True, null=True)

#     time = models.TimeField()
#     payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
#     payment_status = models.CharField(max_length=20, default="Pending")
#     # transaction_id = models.CharField(max_length=100, null=True, blank=True) 
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = ('artist', 'date', 'time')  # ✅ Prevent duplicate bookings

#     def clean(self):
#         """ ✅ Ensure artist is available at the selected time """
#         existing_booking = Booking.objects.filter(
#             artist=self.artist, date=self.date, time=self.time
#         ).exclude(id=self.id)  # Exclude the current instance during updates

#         if existing_booking.exists():
#             raise ValidationError(f"{self.artist.first_name} is already booked at this time.")

#     def save(self, *args, **kwargs):
#         self.clean()  # ✅ Ensure validation before saving
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.client.first_name} booked {self.artist.first_name} for {self.service.service_name} on {self.date} using {self.payment_method}"

# from django.core.exceptions import ValidationError
# from django.db import models
# from django.utils.timezone import now

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
#     service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
#     date = models.DateField()
#     time = models.TimeField()
#     payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
#     payment_status = models.CharField(max_length=20, default="Pending")
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
#     latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Store latitude
#     longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # Store longitude
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         unique_together = ('artist', 'date', 'time')  # ✅ Prevent duplicate bookings

#     def clean(self):
#         """ ✅ Ensure artist is available at the selected time if the booking is not cancelled """
#         if self.status != "Cancelled":
#             existing_booking = Booking.objects.filter(
#                 artist=self.artist, date=self.date, time=self.time
#             ).exclude(id=self.id)  # Exclude the current instance during updates

#             if existing_booking.exists():
#                 raise ValidationError(f"{self.artist.first_name} is already booked at this time.")

#     def save(self, *args, **kwargs):
#         self.clean()  # ✅ Ensure validation before saving
#         super().save(*args, **kwargs)

#         # ✅ When booking is created, mark the slot as booked
#         if self.status in ["Pending", "Confirmed"]:
#             ServiceAvailability.objects.filter(
#                 service=self.service,
#                 available_date=self.date,
#                 available_time=self.time
#             ).update(is_booked=True)

#         # ✅ When booking is cancelled, make the slot available again
#         elif self.status == "Cancelled":
#             ServiceAvailability.objects.filter(
#                 service=self.service,
#                 available_date=self.date,
#                 available_time=self.time
#             ).update(is_booked=False)

#     def __str__(self):
#         return f"{self.client.first_name} booked {self.artist.first_name} for {self.service.service_name} on {self.date} using {self.payment_method}"
from django.db import models
from django.contrib.auth import get_user_model

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
    time = models.TimeField()
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")
    payment_status = models.CharField(max_length=20, default="Pending")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Pending")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # ✅ Allow 6 decimal places
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)  # ✅ Allow 6 decimal places
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('artist', 'date', 'time')  # ✅ Prevent duplicate bookings

    def __str__(self):
        return f"{self.client.first_name} booked {self.artist.first_name} for {self.service.service_name} on {self.date} using {self.payment_method}"


class ServiceAvailability(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="availability")

    available_date = models.DateField()
    available_time = models.TimeField()
    is_booked = models.BooleanField(default=False)  # ✅ Ensure this field exists

    class Meta:
        unique_together = ('service', 'available_date', 'available_time')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.service} - {self.available_date} {self.available_time} - {'Booked' if self.is_booked else 'Available'}"


    def mark_as_booked(self):
        """ ✅ Mark the slot as booked when a new booking is created """
        self.is_booked = True
        self.save()

    def mark_as_available(self):
        """ ✅ Mark the slot as available again when a booking is cancelled """
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
    content = models.TextField()  # ✅ Stores the about us content

    def __str__(self):
        return self.title  # ✅ Display title in admin panel


from django.db import models

class ContactUsPage(models.Model):
    title = models.CharField(max_length=255, default="Contact Us")
    content = models.TextField()  # ✅ Editable contact page content from admin
    email = models.EmailField()  # ✅ Admin email for contact

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
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="artist_reviews")  # ✅ Link to artist
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="service_reviews", null=True, blank=True)  # ✅ Allow NULL
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} reviewed {self.artist.first_name} - {self.rating} Stars"


