from django.contrib import admin
from .models import User, Booking, Service, AboutUs  # ✅ Import all your models

# ✅ Register all models in Django Admin
admin.site.register(User)
admin.site.register(Booking)
admin.site.register(Service)


admin.site.register(AboutUs)  # ✅ Register About Us model
from django.contrib import admin
from .models import ContactUsPage, ContactMessage

admin.site.register(ContactUsPage)  # ✅ Editable contact page content
admin.site.register(ContactMessage)  # ✅ Stores user-submitted messages
