from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import User, Booking
from .views import approve_artist  # ✅ Import the approval function

class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'is_artist', 'is_verified', 'is_approved', 'is_active', 'approve_button')
    list_filter = ('is_artist', 'is_verified', 'is_approved', 'is_active')
    search_fields = ('email', 'phone')
    ordering = ('email',)

    # ✅ Custom "Approve" Button
    def approve_button(self, obj):
        if not obj.is_approved:
            return format_html('<a class="button" href="approve/{}/">Approve</a>', obj.id)
        return "Approved"
    approve_button.short_description = "Approve Artist"
    approve_button.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('approve/<int:artist_id>/', self.admin_site.admin_view(approve_artist), name='approve_artist'),
        ]
        return custom_urls + urls

    # ✅ Remove 'username' from Admin form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('phone', 'profile_image', 'city')}),
        ('Permissions', {'fields': ('is_active', 'is_verified', 'is_artist', 'is_approved', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}), 
    )

    # ✅ Remove 'username' from the Add User Form in Admin Panel
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_artist', 'is_verified', 'is_approved', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(User, CustomUserAdmin)

class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'artist', 'service', 'date', 'start_time', 'end_time', 'status', 'payment_method')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('client__email', 'artist__email', 'service__service_name')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(Booking, BookingAdmin)
