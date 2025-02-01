from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True, null=True, blank=True)  # Allow blank username
    email = models.EmailField(unique=True)  # Email as the unique identifier
    phone = models.CharField(max_length=15, unique=True)
    password = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_artist = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)  # ✅ Stores OTP
    city = models.CharField(max_length=100, null=True, blank=True)
    works_at = models.CharField(max_length=255, null=True, blank=True)
    experience_years = models.IntegerField(default=0, null=True, blank=True)
    training_certificate = models.FileField(upload_to='certificates/', null=True, blank=True)

    USERNAME_FIELD = "email"  # ✅ Login using email instead of username
    REQUIRED_FIELDS = []  # ✅ Don't require username

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








class Service(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to artist
    service_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_date = models.DateField()
    available_time = models.TimeField()
    duration = models.CharField(max_length=50, default="30 mins")  # ✅ Added duration field
    description = models.TextField(blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.service_name} ({self.duration}) - {self.artist.first_name}"










from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # ✅ Track read status


    def __str__(self):
        return f"{self.sender.first_name} to {self.receiver.first_name}: {self.message[:30]}"
    


class Booking(models.Model):
    PAYMENT_CHOICES = [
        ("khalti", "Khalti"),
        ("cod", "Cash on Delivery"),
    ]
    artist = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="client_bookings")
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default="cod")  # ✅ Add payment method
    date = models.DateField()
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)  # ✅ Link to Service

    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.client.first_name} booked {self.artist.first_name} for {self.service.service_name} on {self.date} using {self.payment_method}"