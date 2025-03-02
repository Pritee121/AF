from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import artist_list
from .views import artist_detail
from .views import book_artist
from .views import bookings
from .views import update_booking_status
from .views import booking_history
from .views import aboutus
from .views import contact_us
from .views import add_review
from .views import delete_work
from .views import delete_service, edit_service
from .views import availability_status, toggle_availability
from .views import cancel_booking
from django.contrib.auth import views as auth_views
 # Ensure you import the view
from django.urls import path
 # Import the chat_room view
from django.urls import path
from .views import update_work
from django.urls import path
# from .views import get_available_slots
from .views import get_available_dates, get_available_times
from .views import user_profile
from .views import artist_profile
from .views import edit_review
from .views import reply_to_review
from .views import edit_review_reply, delete_review_reply
from .views import artist_certificates, edit_certificate, delete_certificate
from .views import service_schedule 
from .views import get_notifications
from .views import get_notifications, mark_notifications_read
from .views import working_time_view, delete_working_time 
from .views import get_service_workdays
 # Import the correct view


urlpatterns = [
    path('get_service_workdays/<int:service_id>/', get_service_workdays, name='get_service_workdays'),
    path('delete-working-time/<int:time_id>/', delete_working_time, name='delete_working_time'),
     path('working-time/', working_time_view, name='working_time'),
     path('service-schedule/', service_schedule, name='service_schedule'),
    path('delete-schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
    path('service-schedule/', service_schedule, name='service_schedule'),  # ✅ Define the URL
       path('week-schedule/', views.week_schedule_view, name='week_schedule'),
    # User Authentication
    path("certificates/", artist_certificates, name="artist_certificates"),
    path("certificates/edit/<int:certificate_id>/", edit_certificate, name="edit_certificate"),
    path("certificates/delete/<int:certificate_id>/", delete_certificate, name="delete_certificate"),
    path('edit-review-reply/<int:review_id>/', edit_review_reply, name='edit_review_reply'),
    path('delete-review-reply/<int:review_id>/', delete_review_reply, name='delete_review_reply'),
     path("reply-review/<int:review_id>/", reply_to_review, name="reply_to_review"),
    path('', views.register_page, name='register'),
    path('register-normal/', views.register_normal, name='register_normal'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.login_page, name='login'),
    path('home/', views.home_page, name='home'),
    # Artist Authentication
    path('register-artists/', views.register_artists, name='register_artists'),
    path('artist-login/', views.artist_login, name='artist_login'),
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('artist-logout/', views.artist_logout, name='artist_logout'),
    path("booking-history/", views.booking_history, name="booking_history"),
    # Work Management
    path('add-work/', views.add_work, name='add_work'),
    # Service Management
    path('services/', views.services, name='services'),
    path('add-service/', views.add_service, name='add_service'),
    path('artists/', artist_list, name='artist_list'),
    path('artist/<int:artist_id>/', artist_detail, name='artist_detail'),  # Dynamic artist page
    path('book/<int:artist_id>/', book_artist, name='book_artist'),
    path('bookings/', bookings, name='bookings'),
    path("update-booking-status/<int:booking_id>/", update_booking_status, name="update_booking_status"),
    path("about-us/", aboutus, name="aboutus"),  # Route for About Us page
    path("contact-us/", contact_us, name="contactus"),
    path('artist/<int:artist_id>/review/', views.add_review, name='add_review'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('work/delete/<int:work_id>/', delete_work, name='delete_work'),  # New URL pattern
    path("service/<int:service_id>/delete/", delete_service, name="delete_service"),
    path("services/edit/<int:service_id>/", views.edit_service, name="edit_service"),  
    path("availability/", availability_status, name="availability_status"),  # New URL
    path("cancel-booking/<int:booking_id>/",cancel_booking, name="cancel_booking"),
    path("availability/toggle/", toggle_availability, name="toggle_availability"),
     #Password Reset URLs
    path('artist/password_reset/', 
         auth_views.PasswordResetView.as_view(template_name="accounts/password_reset.html"), 
         name='password_reset'),
    path('artist/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), 
         name='password_reset_done'),
    path('artist/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"), 
         name='password_reset_confirm'),
    path('artist/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), 
         name='password_reset_complete'),
    path('artist/password_reset/', 
         auth_views.PasswordResetView.as_view(template_name="accounts/artist_password_reset.html"), 
         name='artist_password_reset'),
    path('update-work/<int:work_id>/', update_work, name='update_work'),
    path('artist/password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/artist_password_reset_done.html"), 
         name='artist_password_reset_done'),
    path('artist/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="accounts/artist_password_reset_confirm.html"), 
         name='artist_password_reset_confirm'),
    path('artist/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/artist_password_reset_complete.html"), 
         name='artist_password_reset_complete'),
#     path("get-available-slots/<int:artist_id>/", get_available_slots, name="get_available_slots"),
          path('update-work/<int:work_id>/', update_work, name='update_work'),
    path("get-available-dates/<int:artist_id>/", get_available_dates, name="get_available_dates"),
    path("get-available-times/<int:artist_id>/", views.get_available_times, name="get_available_times"),
    path("certificates/", views.certificates_page, name="certificates"),  #Make sure the name is 'certificates'
    path('user/profile/', user_profile, name='user_profile'),
    path('artist/profile/', artist_profile, name='artist_profile'),
    path("edit-review/<int:review_id>/", edit_review, name="edit_review"),
      path('customize-booking/', views.customize_booking, name='customize_booking'),
      path('process-booking/', views.process_booking, name='process_booking'),
       path('booking-location/', views.booking_location, name='booking_location'),
         path('get-notifications/', get_notifications, name='get_notifications'),
         path("mark-notifications-read/", mark_notifications_read, name="mark_notifications_read"),
]

#Serve media files during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





    