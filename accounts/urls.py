# # from django.urls import path
# # from . import views
# # from .views import register_artists, artist_login, artist_dashboard, artist_profile, artist_logout, add_work
# # urlpatterns = [
# #     path('', views.register_page, name='register'),
# #     path('register-normal/', views.register_normal, name='register_normal'),
# #     path('verify-otp/', views.verify_otp, name='verify_otp'),
# #     path('login/', views.login_page, name='login'),
# #     path('home/', views.home_page, name='home'),
# #      path('profile/', views.user_profile, name='user_profile'),
# #        path('register-artists/', register_artists, name='register_artists'),
# #     #  path('profile/<int:user_id>/', profile, name='profile'),
# #     path('artist-login/', artist_login, name='artist_login'),
# #      path('artist-dashboard/', artist_dashboard, name='artist_dashboard'),
# #      path('artist-profile/', artist_profile, name='artist_profile'),
# #      path('artist-logout/', artist_logout, name='artist_logout'),
# #       path('add-work/', add_work, name='add_work'),
# # ]

# from django.urls import path
# from . import views
# from django.conf import settings
# from django.conf.urls.static import static
# from django.urls import path
# from . import views
# urlpatterns = [
#     # User Authentication
#     path('', views.register_page, name='register'),
#     path('register-normal/', views.register_normal, name='register_normal'),
#     path('verify-otp/', views.verify_otp, name='verify_otp'),
#     path('login/', views.login_page, name='login'),
#     path('home/', views.home_page, name='home'),
#     path('profile/', views.user_profile, name='user_profile'),

#     # Artist Authentication
#     path('register-artists/', views.register_artists, name='register_artists'),
#     path('artist-login/', views.artist_login, name='artist_login'),
#     path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
#     path('artist-profile/', views.artist_profile, name='artist_profile'),
#     path('artist-logout/', views.artist_logout, name='artist_logout'),
#     path('services/', views.services, name='services'),  # Add this line
#     path('add-service/', views.add_service, name='add_service'),

#     # Work Management
#     path('add-work/', views.add_work, name='add_work'),
# ]
# # ✅ Add this only for development mode
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import artist_list
from .views import artist_detail
from .views import chat_with_artist
from .views import chat_with_artist, send_message
from django.urls import path
from .views import user_chat, artist_chat, send_message
from .views import book_artist
from .views import bookings
from .views import update_booking_status
from .views import booking_history
from .views import aboutus
from .views import contact_us
from .views import add_review


urlpatterns = [
    # User Authentication
    path('', views.register_page, name='register'),
    path('register-normal/', views.register_normal, name='register_normal'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('login/', views.login_page, name='login'),
    path('home/', views.home_page, name='home'),
    path('profile/', views.user_profile, name='user_profile'),

    # Artist Authentication
    path('register-artists/', views.register_artists, name='register_artists'),
    path('artist-login/', views.artist_login, name='artist_login'),
    path('artist-dashboard/', views.artist_dashboard, name='artist_dashboard'),
    path('artist-profile/', views.artist_profile, name='artist_profile'),
    path('artist-logout/', views.artist_logout, name='artist_logout'),
    path("booking-history/", booking_history, name="booking_history"),
    # Work Management
    path('add-work/', views.add_work, name='add_work'),

    # Service Management
    path('services/', views.services, name='services'),
    path('add-service/', views.add_service, name='add_service'),
    path('artists/', artist_list, name='artist_list'),
    path('artist/<int:artist_id>/', artist_detail, name='artist_detail'),  # ✅ Dynamic artist page
      path('chat/<int:artist_id>/', chat_with_artist, name='chat_with_artist'),
    #   path('send_message/', send_message, name='send_message'),
      path('chat/user/<int:artist_id>/', user_chat, name='user_chat'),
    path('chat/artist/', artist_chat, name='artist_chat'),
    path('send_message/', send_message, name='send_message'),
    path('book/<int:artist_id>/', book_artist, name='book_artist'),
    path('bookings/', bookings, name='bookings'),
     path("update-booking-status/<int:booking_id>/", update_booking_status, name="update_booking_status"),
      path("about-us/", aboutus, name="aboutus"),  # ✅ Route for About Us page
      path("contact-us/", contact_us, name="contactus"),
      path('artist/<int:artist_id>/review/', add_review, name='add_review'),
       path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),  # ✅ New URL pattern
     
]

# ✅ Serve media files during development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
