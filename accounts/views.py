from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash, authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from .models import User, Work, Service
from .forms import (
    ProfileUpdateForm, RegistrationForm, LoginForm, 
    ArtistRegisterForm, OTPForm, ServiceForm
)
import random
from .recommendations import recommend_services_ai_price_band



# ✅ Registration Page
def register_page(request):
    return render(request, 'accounts/register.html')

# ✅ Normal User Registration & OTP Verification
def register_normal(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            otp = str(random.randint(100000, 999999))
            user = form.save(commit=False)
            user.password = make_password(form.cleaned_data['password'])  
            user.otp = otp
            user.save()

            # ✅ Send OTP Email
            send_mail(
                'Your OTP for Artist Finder', 
                f'Your OTP is {otp}', 
                'admin@artistfinder.com', 
                [user.email]
            )

            request.session['user_id'] = user.id  
            return redirect('verify_otp')

    return render(request, 'accounts/register_normal.html', {'form': RegistrationForm()})

# ✅ OTP Verification
def verify_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('register')

    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid() and form.cleaned_data['otp'] == user.otp:
            user.is_verified = True
            user.otp = None
            user.save()
            return redirect('artist_login' if user.is_artist else 'login')
        else:
            form.add_error('otp', 'Invalid OTP')

    return render(request, 'accounts/verify_otp.html', {'form': OTPForm()})




def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None and not user.is_artist:
                login(request, user)
                request.session['user_type'] = 'client'  # Ensure session stores user type
                return redirect('home')
            else:
                form.add_error(None, 'Invalid email or password.')

    return render(request, 'accounts/login.html', {'form': LoginForm()})





from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .forms import LoginForm

def artist_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is None:
                form.add_error(None, 'Invalid email or password.')
                return render(request, "accounts/artist_login.html", {'form': form})

            if user.is_artist:
                if not user.is_verified:
                    form.add_error(None, 'Account not verified. Please verify via OTP.')
                    return render(request, "accounts/artist_login.html", {'form': form})

                if not user.is_approved:  # ✅ Check if admin has approved the artist
                    form.add_error(None, 'Your account is not approved yet.')
                    return render(request, "accounts/artist_login.html", {'form': form})

                login(request, user)
                request.session['user_type'] = 'artist'
                return redirect('artist_dashboard')

            else:
                form.add_error(None, 'Invalid email or password.')

    return render(request, "accounts/artist_login.html", {'form': LoginForm()})

# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Avg, Count, Q  # ✅ Import Avg, Count, and Q
# from .models import User, Booking, Review

# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

#     # ✅ Step 1: Get All Artists (Keep Unavailable in Main List)
#     artists = User.objects.filter(is_artist=True)  # Keep all artists (available & unavailable)
    
#     if query:
#         artists = artists.filter(city__icontains=query)

#     # ✅ Step 2: Annotate Artists with Average Rating
#     artists = artists.annotate(
#         avg_rating=Avg('artist_reviews__rating'),  # ✅ Correct annotation
#         appointment_count=Count('bookings', filter=Q(bookings__status="Confirmed"))
#     )

#     # ✅ Step 3: Sorting Logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating')  # ✅ Sort by average rating
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count')  # ✅ Sort by confirmed appointments

#     # ✅ Step 4: Paginate Artists (10 per page)
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     # ✅ Step 5: Fetch Booked Artists by User
#     user_bookings = Booking.objects.filter(client=user, status="Confirmed").order_by('-date')
#     booked_artist_ids = user_bookings.values_list('artist_id', flat=True)

#     # ✅ Step 6: AI-BASED RECOMMENDATION LOGIC (ONLY AVAILABLE ARTISTS)
#     recommended_artists = []

#     if booked_artist_ids:
#         # ✅ Find users who booked the same artists
#         similar_users = Booking.objects.filter(artist_id__in=booked_artist_ids).values_list("client_id", flat=True).distinct()

#         if similar_users:
#             recommended_artists = User.objects.filter(
#                 is_artist=True,
#                 is_available=True,
#                 bookings__client_id__in=similar_users
#             ).exclude(id__in=booked_artist_ids).annotate(
#                 booking_count=Count("bookings")
#             ).order_by("-booking_count")[:5]

#     # ✅ Step 7: Check Latest Booking City (ONLY AVAILABLE ARTISTS)
#     if not recommended_artists and user_bookings.exists():
#         latest_booking = user_bookings.first()
#         latest_artist_city = latest_booking.artist.city

#         recommended_artists = User.objects.filter(
#             is_artist=True,
#             is_available=True,
#             city=latest_artist_city
#         ).exclude(id=user.id).annotate(avg_rating=Avg('artist_reviews__rating')).order_by('-avg_rating')[:5]

#     # ✅ Step 8: Fallback to Artists from the Same City (ONLY AVAILABLE ARTISTS)
#     if not recommended_artists and user.city:
#         recommended_artists = User.objects.filter(
#             is_artist=True,
#             is_available=True,
#             city=user.city
#         ).exclude(id=user.id).annotate(avg_rating=Avg('artist_reviews__rating')).order_by('-avg_rating')[:5]

#     # ✅ Step 9: Fallback to Top-Rated Artists (ONLY AVAILABLE ARTISTS)
#     if not recommended_artists:
#         recommended_artists = artists.filter(is_available=True).order_by('-avg_rating')[:5]

#     # ✅ Fetch Latest Artist Reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]
#     artists = User.objects.filter(is_artist=True).annotate(
#         appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))
#     )
#     return render(request, "accounts/home.html", {
#         "artists": page_obj,  # ✅ Keep all artists (available & unavailable)
#         "recommended_artists": recommended_artists,  # ✅ Remove unavailable artists from recommendations
#         "artist_reviews": artist_reviews,  # Latest Artist Reviews
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": list(booked_artist_ids),  # List of booked artist IDs
#         "sort_by": sort_by,
#     })


# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Avg, Count, Q
# from .models import User, Booking, Review

# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")  # Default: sort by rating

#     # ✅ Step 1: Fetch all artists (available & unavailable)
#     artists = User.objects.filter(is_artist=True)

#     if query:
#         artists = artists.filter(city__icontains=query)

#     # ✅ Step 2: Annotate Artists with Average Rating & Completed Appointments
#     artists = artists.annotate(
#         avg_rating=Avg('artist_reviews__rating'),  # ✅ Fetch avg rating
#         appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))  # ✅ Count only "Completed" bookings
#     )

#     # ✅ Step 3: Sorting Logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating')
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count')

#     # ✅ Step 4: Paginate Artists (10 per page)
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     # ✅ Step 5: Fetch Booked Artists by the User
#     user_bookings = Booking.objects.filter(client=user, status="Confirmed").order_by('-date')
#     booked_artist_ids = list(user_bookings.values_list('artist_id', flat=True))

#     # ✅ Step 6: AI-BASED RECOMMENDATION SYSTEM
#     recommended_artists = []

#     if booked_artist_ids:
#         # ✅ Find users who booked the same artists
#         similar_users = Booking.objects.filter(artist_id__in=booked_artist_ids).values_list("client_id", flat=True).distinct()

#         if similar_users:
#             recommended_artists = User.objects.filter(
#                 is_artist=True,
#                 is_available=True,
#                 bookings__client_id__in=similar_users
#             ).exclude(id__in=booked_artist_ids).annotate(
#                 booking_count=Count("bookings")
#             ).order_by("-booking_count")[:5]

#     # ✅ Step 7: Fallback to Latest Booking's City (if no recommendations found)
#     if not recommended_artists and user_bookings.exists():
#         latest_booking = user_bookings.first()
#         recommended_artists = User.objects.filter(
#             is_artist=True,
#             is_available=True,
#             city=latest_booking.artist.city
#         ).exclude(id=user.id).annotate(avg_rating=Avg('artist_reviews__rating')).order_by('-avg_rating')[:5]

#     # ✅ Step 8: Fallback to User's Own City
#     if not recommended_artists and user.city:
#         recommended_artists = User.objects.filter(
#             is_artist=True,
#             is_available=True,
#             city=user.city
#         ).exclude(id=user.id).annotate(avg_rating=Avg('artist_reviews__rating')).order_by('-avg_rating')[:5]

#     # ✅ Step 9: Fallback to Top-Rated Available Artists
#     if not recommended_artists:
#         recommended_artists = User.objects.filter(
#             is_artist=True,
#             is_available=True
#         ).annotate(avg_rating=Avg('artist_reviews__rating')).order_by('-avg_rating')[:5]

#     # ✅ Step 10: Fetch Latest Artist Reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

#     # ✅ Final Data Rendering
#     return render(request, "accounts/home.html", {
#         "artists": page_obj,  # ✅ Paginated artist list
#         "recommended_artists": recommended_artists,  # ✅ Remove unavailable artists from recommendations
#         "artist_reviews": artist_reviews,  # Latest Artist Reviews
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": booked_artist_ids,  # ✅ List of booked artist IDs
#         "sort_by": sort_by,
#     }) ajaaa

# from django.utils.timezone import now
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Avg, Count, Q
# from .models import User, Booking, Review

# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

#     # ✅ Step 1: Print Current Date & Time for Debugging
#     current_date = now().date()
#     current_time = now().time()
#     print("🔥 Current Date:", current_date)
#     print("🔥 Current Time:", current_time)

#     # ✅ Step 2: Fetch all artists
#     artists = User.objects.filter(is_artist=True).annotate(
#         avg_rating=Avg('artist_reviews__rating'),
#         appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))
#     )

#     if query:
#         artists = artists.filter(city__icontains=query)

#     # ✅ Step 3: Sorting Logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating', '-appointment_count')
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count', '-avg_rating')

#     # ✅ Step 4: Paginate Artists (10 per page) ✅ FIXED PAGE OBJECT
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page") or 1
#     page_obj = paginator.get_page(page_number)  # ✅ THIS LINE FIXES THE ERROR

#     # ✅ Step 5: Print All User Bookings for Debugging
#     all_user_bookings = Booking.objects.filter(client=user).values('id', 'date', 'end_time', 'status')
#     print("🔍 All User Bookings:", list(all_user_bookings))

#     # ✅ Step 6: Fetch Completed Bookings (Check Date & Time)
#     completed_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date__lt=current_date  # ✅ Booking date is in the past
#     ).values_list('artist_id', flat=True)

#     # ✅ If today's date, check if end_time has passed
#     ongoing_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date=current_date,
#         end_time__lte=current_time  # ✅ Booking time has ended
#     ).values_list('artist_id', flat=True)

#     # ✅ Combine both completed and finished bookings
#     booked_artist_ids = list(completed_bookings) + list(ongoing_bookings)

#     # 🔥 Debugging: Check what bookings are fetched
#     print("✅ Completed Bookings:", list(completed_bookings))
#     print("✅ Ongoing Bookings (Today):", list(ongoing_bookings))
#     print("✅ Final Booked Artists List:", booked_artist_ids)

#     # ✅ Step 7: Fetch Recommended Artists
#     recommended_artists = User.objects.filter(
#         is_artist=True, is_available=True
#     ).exclude(id__in=booked_artist_ids).annotate(
#         avg_rating=Avg('artist_reviews__rating')
#     ).order_by('-avg_rating')[:5]

#     # ✅ Step 8: Fetch Latest Artist Reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

#     return render(request, "accounts/home.html", {
#         "artists": page_obj,  # ✅ FIXED THIS LINE
#         "recommended_artists": recommended_artists,
#         "artist_reviews": artist_reviews,
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": booked_artist_ids,
#         "sort_by": sort_by,
#     })





# from django.utils.timezone import now, localtime
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Avg, Count, Q
# from pytz import timezone
# from .models import User, Booking, Review

# NEPAL_TZ = timezone('Asia/Kathmandu')  # ✅ Set Nepal timezone

# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

#     # ✅ Convert to Nepal Time
#     current_datetime_nepal = localtime(now(), NEPAL_TZ)
#     current_date = current_datetime_nepal.date()
#     current_time = current_datetime_nepal.time()

#     # ✅ Debugging: Print Date & Time in both UTC and Nepal Time
#     print("🔥 UTC Date & Time:", now())
#     print("🔥 Nepal Date:", current_date)
#     print("🔥 Nepal Time:", current_time)

#     # ✅ Step 2: Fetch all artists and annotate with rating & completed appointments
#     artists = User.objects.filter(is_artist=True).annotate(
#         avg_rating=Avg('artist_reviews__rating'),
#         appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))
#     )

#     if query:
#         artists = artists.filter(city__icontains=query)

#     # ✅ Step 3: Sorting Logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating', '-appointment_count')
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count', '-avg_rating')

#     # ✅ Step 4: Paginate Artists (10 per page)
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page") or 1
#     page_obj = paginator.get_page(page_number)

#     # ✅ Step 5: Print All User Bookings for Debugging
#     all_user_bookings = Booking.objects.filter(client=user).values('id', 'date', 'end_time', 'status')
#     print("🔍 All User Bookings:", list(all_user_bookings))

#     # ✅ Step 6: Fetch Completed Bookings (Check Date & Time in Nepal)
#     completed_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date__lt=current_date  # ✅ Booking date is in the past
#     ).values_list('artist_id', flat=True)

#     # ✅ Check ongoing bookings only if time has passed in Nepal
#     ongoing_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date=current_date,
#         end_time__lte=current_time  # ✅ Booking time has ended (in Nepal)
#     ).values_list('artist_id', flat=True)

#     # ✅ Combine completed and finished bookings
#     booked_artist_ids = list(completed_bookings) + list(ongoing_bookings)

#     # 🔥 Debugging: Check what bookings are fetched
#     print("✅ Completed Bookings:", list(completed_bookings))
#     print("✅ Ongoing Bookings (Today):", list(ongoing_bookings))
#     print("✅ Final Booked Artists List:", booked_artist_ids)

#     # ✅ Step 7: Fetch Recommended Artists
#     recommended_artists = User.objects.filter(
#         is_artist=True, is_available=True
#     ).exclude(id__in=booked_artist_ids).annotate(
#         avg_rating=Avg('artist_reviews__rating')
#     ).order_by('-avg_rating')[:5]

#     # ✅ Step 8: Fetch Latest Artist Reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

#     return render(request, "accounts/home.html", {
#         "artists": page_obj,  # ✅ FIXED PAGINATION
#         "recommended_artists": recommended_artists,
#         "artist_reviews": artist_reviews,
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": booked_artist_ids,
#         "sort_by": sort_by,
        
#     }) aja ko 

# from django.utils.timezone import now, localtime
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Avg, Count, Q
# from pytz import timezone
# from collections import Counter
# from decimal import Decimal
# from .models import User, Booking, Review, Service  # ✅ Include Service model

# NEPAL_TZ = timezone('Asia/Kathmandu')  # ✅ Set Nepal timezone

# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

#     # ✅ Convert to Nepal Time
#     current_datetime_nepal = localtime(now(), NEPAL_TZ)
#     current_date = current_datetime_nepal.date()
#     current_time = current_datetime_nepal.time()

#     # ✅ Debugging: Print Date & Time in both UTC and Nepal Time
#     print("🔥 UTC Date & Time:", now())
#     print("🔥 Nepal Date:", current_date)
#     print("🔥 Nepal Time:", current_time)

#     # ✅ Step 2: Fetch all artists and annotate with rating & completed appointments
#     artists = User.objects.filter(is_artist=True).annotate(
#         avg_rating=Avg('artist_reviews__rating'),
#         appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))
#     )

#     if query:
#         artists = artists.filter(city__icontains=query)

#     # ✅ Step 3: Sorting Logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating', '-appointment_count')
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count', '-avg_rating')

#     # ✅ Step 4: Paginate Artists (10 per page)
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page") or 1
#     page_obj = paginator.get_page(page_number)

#     # ✅ Step 5: Print All User Bookings for Debugging
#     all_user_bookings = Booking.objects.filter(client=user).values('id', 'date', 'end_time', 'status')
#     print("🔍 All User Bookings:", list(all_user_bookings))

#     # ✅ Step 6: Fetch Completed Bookings (Check Date & Time in Nepal)
#     completed_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date__lt=current_date
#     ).values_list('artist_id', flat=True)

#     ongoing_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date=current_date,
#         end_time__lte=current_time
#     ).values_list('artist_id', flat=True)

#     booked_artist_ids = list(completed_bookings) + list(ongoing_bookings)

#     print("✅ Completed Bookings:", list(completed_bookings))
#     print("✅ Ongoing Bookings (Today):", list(ongoing_bookings))
#     print("✅ Final Booked Artists List:", booked_artist_ids)

#     # ✅ Step 7: Fetch Recommended Artists
#     recommended_artists = User.objects.filter(
#         is_artist=True, is_available=True
#     ).exclude(id__in=booked_artist_ids).annotate(
#         avg_rating=Avg('artist_reviews__rating')
#     ).order_by('-avg_rating')[:5]

#     # ✅ Step 8: Fetch Latest Artist Reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

#     # ✅ Step 9: Recommended Services Based on Frequent Booking Price
#     recommended_services = []
#     bookings = Booking.objects.filter(client=user, status="Confirmed", service__isnull=False)

#     prices = [float(b.service.price) for b in bookings if b.service]
#     price_counts = Counter(prices)

#     if price_counts:
#         most_common_price, _ = price_counts.most_common(1)[0]
#         price_range_low = Decimal(most_common_price - 500)
#         price_range_high = Decimal(most_common_price + 500)

#         recommended_services = Service.objects.filter(
#             price__gte=price_range_low,
#             price__lte=price_range_high
#         ).exclude(artist=user)[:6]

#     # ✅ Final render
#     return render(request, "accounts/home.html", {
#         "artists": page_obj,
#         "recommended_artists": recommended_artists,
#         "artist_reviews": artist_reviews,
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": booked_artist_ids,
#         "sort_by": sort_by,
#         "recommended_services": recommended_services,  # ✅ Add this to context
#     })

from django.utils.timezone import now, localtime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from pytz import timezone
from .models import User, Booking, Review, Service
from .recommendations import recommend_services_ai_price_band


 # ✅ Import your AI logic

NEPAL_TZ = timezone('Asia/Kathmandu')

# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")

#     # Convert to Nepal Time
#     current_datetime_nepal = localtime(now(), NEPAL_TZ)
#     current_date = current_datetime_nepal.date()
#     current_time = current_datetime_nepal.time()

#     # Fetch artists with rating and appointment count
#     artists = User.objects.filter(is_artist=True).annotate(
#         avg_rating=Avg('artist_reviews__rating'),
#         appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))
#     )

#     if query:
#         artists = artists.filter(city__icontains=query)

#     # Sorting Logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating', '-appointment_count')
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count', '-avg_rating')

#     # Pagination
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page") or 1
#     page_obj = paginator.get_page(page_number)

#     # Booked Artists (Completed or Finished Today)
#     completed_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date__lt=current_date
#     ).values_list('artist_id', flat=True)

#     ongoing_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date=current_date,
#         end_time__lte=current_time
#     ).values_list('artist_id', flat=True)

#     booked_artist_ids = list(completed_bookings) + list(ongoing_bookings)

#     # Recommended Artists (not already booked)
#     recommended_artists = User.objects.filter(
#         is_artist=True,
#         is_available=True
#     ).exclude(id__in=booked_artist_ids).annotate(
#         avg_rating=Avg('artist_reviews__rating')
#     ).order_by('-avg_rating')[:5]

#     # Latest Artist Reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

#     # ✅ AI-Based Recommended Services
#     # ✅ Call once, no comma
#     recommended_services = recommend_services_ai_price_band(user)

# # ✅ Use it in the context
#     return render(request, "accounts/home.html", {
#     "artists": page_obj,
#     "recommended_artists": recommended_artists,
#     "artist_reviews": artist_reviews,
#     "query": query,
#     "message": "No artists found in this city." if not artists.exists() else "",
#     "booked_artists": booked_artist_ids,
#     "sort_by": sort_by,
#     "recommended_services": recommended_services,
# })
# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")

#     # Nepal timezone
#     current_datetime_nepal = localtime(now(), NEPAL_TZ)
#     current_date = current_datetime_nepal.date()
#     current_time = current_datetime_nepal.time()

#     # ✅ Update past bookings to Completed
#     Booking.objects.filter(
#         status="Confirmed",
#         date__lt=current_date
#     ).update(status="Completed")

#     Booking.objects.filter(
#         status="Confirmed",
#         date=current_date,
#         end_time__lt=current_time
#     ).update(status="Completed")

#     # Filter artists
#     artists = User.objects.filter(is_artist=True).annotate(
#         avg_rating=Avg('artist_reviews__rating'),
#         appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))
#     )

#     if query:
#         artists = artists.filter(city__icontains=query)

#     # Sorting
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating', '-appointment_count')
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count', '-avg_rating')

#     # Pagination
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page") or 1
#     page_obj = paginator.get_page(page_number)

#     # Booked artist IDs
#     completed_bookings = Booking.objects.filter(
#         client=user,
#         status="Completed"
#     ).values_list('artist_id', flat=True)

#     booked_artist_ids = list(completed_bookings)

#     # Recommended artists (not already booked)
#     recommended_artists = User.objects.filter(
#         is_artist=True,
#         is_available=True
#     ).exclude(id__in=booked_artist_ids).annotate(
#         avg_rating=Avg('artist_reviews__rating')
#     ).order_by('-avg_rating')[:5]

#     # Recent reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

#     # AI recommended services
#     recommended_services = recommend_services_ai_price_band(user)

#     return render(request, "accounts/home.html", {
#         "artists": page_obj,
#         "recommended_artists": recommended_artists,
#         "artist_reviews": artist_reviews,
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": booked_artist_ids,
#         "sort_by": sort_by,
#         "recommended_services": recommended_services,
#     })

from django.utils.timezone import now, localtime
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q
from pytz import timezone
from .models import User, Booking, Review, Service
from .recommendations import recommend_services_ai_price_band

NEPAL_TZ = timezone('Asia/Kathmandu')


@login_required(login_url='login')
def home_page(request):
    user = request.user
    query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "rating")

    # Get current Nepal date and time
    current_datetime_nepal = localtime(now(), NEPAL_TZ)
    current_date = current_datetime_nepal.date()
    current_time = current_datetime_nepal.time()

    # ✅ Update bookings to 'Completed' if past their end time
    Booking.objects.filter(
        status="Confirmed",
        date__lt=current_date
    ).update(status="Completed")

    Booking.objects.filter(
        status="Confirmed",
        date=current_date,
        end_time__lt=current_time
    ).update(status="Completed")

    # ✅ Get all artists with average rating and completed appointment count
    artists = User.objects.filter(is_artist=True).annotate(
        avg_rating=Avg('artist_reviews__rating'),
        appointment_count=Count('bookings', filter=Q(bookings__status="Completed"))
    )

    if query:
        artists = artists.filter(city__icontains=query)

    # ✅ Sort by rating or appointments
    if sort_by == "rating":
        artists = artists.order_by('-avg_rating', '-appointment_count')
    elif sort_by == "appointments":
        artists = artists.order_by('-appointment_count', '-avg_rating')

    # ✅ Paginate artists
    paginator = Paginator(artists, 10)
    page_number = request.GET.get("page") or 1
    page_obj = paginator.get_page(page_number)

    # ✅ Get booked artists (completed only)
    completed_bookings = Booking.objects.filter(
        client=user,
        status="Completed"
    ).values_list('artist_id', flat=True)
    booked_artist_ids = list(completed_bookings)

    # ✅ Recommended Artists Logic
    recommended_artists = list(User.objects.filter(
        is_artist=True,
        is_available=True
    ).exclude(id__in=booked_artist_ids).annotate(
        avg_rating=Avg('artist_reviews__rating')
    ).order_by('-avg_rating')[:5])

    # ✅ Fallback: if no unbooked artists, show top-rated available artists
    if not recommended_artists:
        recommended_artists = list(User.objects.filter(
            is_artist=True,
            is_available=True
        ).annotate(
            avg_rating=Avg('artist_reviews__rating')
        ).order_by('-avg_rating')[:5])

    # ✅ Recent reviews
    artist_reviews = Review.objects.select_related("artist", "user", "service").order_by("-created_at")[:10]

    # ✅ AI Recommended Services
    recommended_services = recommend_services_ai_price_band(user)

    return render(request, "accounts/home.html", {
        "artists": page_obj,
        "recommended_artists": recommended_artists,
        "artist_reviews": artist_reviews,
        "query": query,
        "message": "No artists found in this city." if not artists.exists() else "",
        "booked_artists": booked_artist_ids,
        "sort_by": sort_by,
        "recommended_services": recommended_services,
    })


from django.shortcuts import get_object_or_404, render
from .models import Service

def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, "accounts/service_detail.html", {"service": service})





# from django.utils.timezone import now, localtime
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Avg, Count, Q
# from pytz import timezone
# from .models import User, Booking, Review

# NEPAL_TZ = timezone('Asia/Kathmandu')  # ✅ Set Nepal timezone

# @login_required(login_url='login')
# def home_page(request):
#     user = request.user
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

#     # ✅ Get Nepal Time
#     current_datetime_nepal = localtime(now(), NEPAL_TZ)
#     current_date = current_datetime_nepal.date()
#     current_time = current_datetime_nepal.time()

#     # ✅ Debugging: Print Current Date & Time
#     print("🔥 UTC Time:", now())
#     print("🔥 Nepal Date:", current_date)
#     print("🔥 Nepal Time:", current_time)

#     # ✅ Step 1: Fetch all artists and count only **completed** appointments
#     artists = User.objects.filter(is_artist=True).annotate(
#         avg_rating=Avg('artist_reviews__rating'),
#         appointment_count=Count(
#             'bookings',
#             filter=Q(bookings__status="Confirmed") & (
#                 Q(bookings__date__lt=current_date) |  # ✅ Past completed bookings
#                 Q(bookings__date=current_date, bookings__end_time__lte=current_time)  # ✅ Completed today
#             )
#         )
#     )

#     if query:
#         artists = artists.filter(city__icontains=query)

#     # ✅ Step 2: Sorting Logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating', '-appointment_count')
#     elif sort_by == "appointments":
#         artists = artists.order_by('-appointment_count', '-avg_rating')

#     # ✅ Step 3: Paginate Artists (10 per page)
#     paginator = Paginator(artists, 10)
#     page_number = request.GET.get("page") or 1
#     page_obj = paginator.get_page(page_number)

#     # ✅ Step 4: Fetch Completed Bookings for Users
#     completed_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date__lt=current_date  # ✅ Bookings before today
#     ).values_list('artist_id', flat=True)

#     # ✅ Fetch bookings completed **today** (after end_time has passed)
#     ongoing_bookings = Booking.objects.filter(
#         client=user,
#         status="Confirmed",
#         date=current_date,
#         end_time__lte=current_time  # ✅ Booking time has ended
#     ).values_list('artist_id', flat=True)

#     # ✅ Combine completed and finished bookings
#     booked_artist_ids = list(completed_bookings) + list(ongoing_bookings)

#     # 🔥 Debugging: Check what bookings are fetched
#     print("✅ Completed Bookings:", list(completed_bookings))
#     print("✅ Ongoing Bookings (Today):", list(ongoing_bookings))
#     print("✅ Final Booked Artists List:", booked_artist_ids)

#     # ✅ Step 5: Fetch Recommended Artists (excluding already booked ones)
#     recommended_artists = User.objects.filter(
#         is_artist=True, is_available=True
#     ).exclude(id__in=booked_artist_ids).annotate(
#         avg_rating=Avg('artist_reviews__rating')
#     ).order_by('-avg_rating')[:5]

#     # ✅ Step 6: Fetch Latest Artist Reviews
#     artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

#     return render(request, "accounts/home.html", {
#         "artists": page_obj,  # ✅ FIXED PAGINATION
#         "recommended_artists": recommended_artists,
#         "artist_reviews": artist_reviews,
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": booked_artist_ids,  # ✅ Updated booked artists list
#         "sort_by": sort_by,
#     })


from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import User
import logging

logger = logging.getLogger(__name__)  # ✅ Setup logging

def approve_artist(request, artist_id):
    """ ✅ Admin manually approves an artist and sends an email """
    artist = get_object_or_404(User, id=artist_id, is_artist=True)

    if artist.is_approved:
        messages.warning(request, "This artist is already approved.")
        return redirect("admin:accounts_user_changelist")  # Redirect to admin users list

    # ✅ Approve artist
    artist.is_approved = True
    artist.save()

    # ✅ Send email notification
    try:
        send_mail(
            subject="🎨 Your Artist Account Has Been Approved!",
            message=f"""
            Dear {artist.first_name},

            Your artist account has been approved! 🎉 You can now log in and manage your profile, showcase your work, and accept bookings.

            🌟 Dashboard: https://yourwebsite.com/dashboard

            Best Regards,
            Artist Finder Team
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[artist.email],
            fail_silently=False,
        )
        logger.info(f"✅ Approval email sent to {artist.email}")

    except Exception as e:
        logger.error(f"❌ Error sending approval email to {artist.email}: {str(e)}")
        messages.error(request, f"Error sending email to {artist.email}: {str(e)}")

    messages.success(request, "Artist approved and email sent successfully.")
    return redirect("admin:accounts_user_changelist")  # Redirect back to admin




# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from datetime import datetime, timedelta
# from django.shortcuts import get_object_or_404
# from .models import Booking

# @csrf_exempt
# def cancel_booking(request, booking_id):
#     if request.method == "POST":
#         try:
#             booking = get_object_or_404(Booking, id=booking_id)

#             # ✅ Prevent cancellation if booking is within 24 hours
#             time_left = (booking.date - datetime.today().date()).days
#             if time_left < 1:
#                 return JsonResponse({"error": "You cannot cancel bookings within 24 hours."}, status=400)

#             # ✅ Change booking status
#             booking.status = "Cancelled"
#             booking.save()

#             return JsonResponse({"success": "Booking successfully cancelled."}, status=200)
#         except Exception as e:
#             return JsonResponse({"error": f"Something went wrong: {str(e)}"}, status=500)

#     return JsonResponse({"error": "Invalid request method."}, status=400)
# import json
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
# from .models import Booking

# @csrf_exempt  # ✅ Allow AJAX requests
# def cancel_booking(request, booking_id):
#     if request.method == "POST":
#         try:
#             booking = get_object_or_404(Booking, id=booking_id)

#             if booking.status == "Cancelled":
#                 return JsonResponse({"error": "Booking is already cancelled."}, status=400)

#             # ✅ Mark the booking as cancelled (or delete it)
#             booking.delete()  # ✅ Remove booking from the database (free the time slot)

#             return JsonResponse({"success": "Booking cancelled successfully. The time slot is now available again."})
#         except Exception as e:
#             return JsonResponse({"error": f"Error cancelling booking: {str(e)}"}, status=500)

#     return JsonResponse({"error": "Invalid request"}, status=400)

import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Booking

@csrf_exempt  # ✅ Allow AJAX requests
def cancel_booking(request, booking_id):
    if request.method == "POST":
        try:
            booking = get_object_or_404(Booking, id=booking_id)

            if booking.status == "Cancelled":
                return JsonResponse({"error": "Booking is already cancelled."}, status=400)

            # ✅ Mark the booking as cancelled instead of deleting it
            booking.status = "Cancelled"
            booking.save()

            return JsonResponse({
                "success": "Booking cancelled successfully. The time slot is now marked as cancelled."
            })
        except Exception as e:
            return JsonResponse({"error": f"Error cancelling booking: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



from django.shortcuts import render, get_object_or_404, redirect
from .models import Service
from .forms import ServiceEditForm

def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == "POST":
        form = ServiceEditForm(request.POST, instance=service)
        
        if form.is_valid():
            service.service_name = form.cleaned_data['service_name']
            service.price = form.cleaned_data['price']
            service.description = form.cleaned_data['description']
            service.work_days.set(form.cleaned_data['work_days'])

            # ✅ Update duration & travel time
            service.duration = form.cleaned_data['duration']
            service.travel_time = form.cleaned_data['travel_time']
            
            service.save()
            return redirect('services')

    else:
        form = ServiceEditForm(instance=service)

    return render(request, 'accounts/edit_service.html', {'service_form': form})

import random
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.contrib import messages
from .forms import ArtistRegisterForm
from .models import User, TrainingCertificate

def register_artists(request):
    if request.method == "POST":
        form = ArtistRegisterForm(request.POST, request.FILES)
        training_certificates = request.FILES.getlist("training_certificates")

        if form.is_valid():
            otp = str(random.randint(100000, 999999))
            user = form.save(commit=False)

            if form.cleaned_data.get('password'):
                user.password = make_password(form.cleaned_data['password'])

            user.is_artist = True  
            user.is_verified = False  
            user.is_approved = False  # ✅ Artist needs admin approval
            user.otp = otp  
            user.save()

            # Save multiple certificates
            for certificate in training_certificates:
                TrainingCertificate.objects.create(artist=user, certificate=certificate)

            # Send OTP email
            send_mail(
                'Your OTP for Artist Registration', 
                f'Your OTP is {otp}', 
                'admin@artistfinder.com', 
                [user.email]
            )

            request.session['user_id'] = user.id
            messages.success(request, "Registration successful! Please verify your OTP.")
            return redirect('verify_otp')

        else:
            messages.error(request, "Error in registration. Please check your details.")

    return render(request, 'accounts/register_artists.html', {'form': ArtistRegisterForm()})

# # ✅ Artist Dashboard
# @login_required(login_url='artist_login')
# def artist_dashboard(request):
#     artist = request.user
#     if not artist.is_artist:
#         return redirect('artist_login')

#     works = Work.objects.filter(artist=artist)
#     return render(request, 'accounts/artist_dashboard.html', {'works': works})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from chat.models import ChatRoom, ChatMessage  # ✅ Import from the correct app


@login_required
def artist_dashboard(request):
    # Get all chats where the logged-in user is either a user or an artist
    chats = ChatRoom.objects.filter(user=request.user) | ChatRoom.objects.filter(artist=request.user)

    # Create a dictionary to store unread message counts for each chat
    chat_unread_counts = {}
    for chat in chats:
        unread_count = ChatMessage.objects.filter(chat_room=chat, is_read=False).exclude(sender=request.user).count()
        chat_unread_counts[chat.id] = unread_count  # Store count using chat ID

    return render(request, 'accounts/artist_dashboard.html', {
        'chats': chats,
        'chat_unread_counts': chat_unread_counts,  # Pass this dictionary to the template
    })


def artist_logout(request):
    logout(request)  # ✅ Clears session but NOT password
    request.session.flush()  # ✅ Ensure complete session reset
    return redirect('artist_login')


def user_logout(request):
    logout(request)
    request.session.flush()  # ✅ Clear user type session
    return redirect('login')

# ✅ Add Work
@login_required(login_url='artist_login')
def add_work(request):
    artist = request.user

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if not title or not image:
            return render(request, 'accounts/add_work.html', {'error': "Title and image are required."})

        Work.objects.create(
            artist=artist,
            title=title,
            description=description,
            image=image
        )

        return redirect('artist_dashboard')

    return render(request, 'accounts/add_work.html')

# from django.shortcuts import render, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from .models import Service, Review

# @login_required(login_url='artist_login')  # Ensure user is logged in before accessing services
# def services(request):
#     artist_services = Service.objects.filter(artist=request.user).prefetch_related('service_reviews')  # Efficiently load reviews
#     return render(request, 'accounts/services.html', {'services': artist_services})


# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Service

# @login_required(login_url='artist_login')
# def services(request):
#     artist_services = Service.objects.filter(artist=request.user).prefetch_related('service_reviews', 'work_days')  

#     service_schedules = {}  # Store week days and slots for each service
#     for service in artist_services:
#         weekly_schedule = {}  # Store schedule per week day

#         for work_day in service.work_days.all():  # Loop through assigned work days
#             weekly_schedule[work_day.day] = service.generate_slots_for_day(work_day)  # Get slots for each day

#         service_schedules[service.id] = weekly_schedule  # Store data

#     return render(request, 'accounts/services.html', {
#         'services': artist_services,
#         'service_schedules': service_schedules
#     })
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from .models import Service, Review

@login_required(login_url='artist_login')
def services(request):
    artist_services = Service.objects.filter(artist=request.user).prefetch_related('service_reviews', 'work_days')  

    service_schedules = {}  # Store week days and slots for each service
    service_reviews = {}  # Store reviews for each service

    for service in artist_services:
        # ✅ Get Work Schedule
        weekly_schedule = {}  # Store schedule per week day
        for work_day in service.work_days.all():
            weekly_schedule[work_day.day] = service.generate_slots_for_day(work_day)  

        service_schedules[service.id] = weekly_schedule  

        # ✅ Fetch Reviews for Service
        service_reviews[service.id] = list(service.service_reviews.all())  # ✅ Use the correct related name

    return render(request, 'accounts/services.html', {
        'services': artist_services,
        'service_schedules': service_schedules,
        'service_reviews': service_reviews  # ✅ Pass reviews to the template
    })







# from django.shortcuts import render, redirect
# from .models import Service, ServiceAvailability
# from .forms import ServiceForm, ServiceAvailabilityFormSet
# from django.contrib.auth.decorators import login_required

# @login_required
# def add_service(request):
#     if request.method == "POST":
#         service_form = ServiceForm(request.POST)
#         formset = ServiceAvailabilityFormSet(request.POST)

#         if service_form.is_valid() and formset.is_valid():
#             # ✅ Create and Save the Service First
#             service = service_form.save(commit=False)
#             service.artist = request.user  # Assign artist before saving
#             service.save()

#             # ✅ Save all availability slots related to the service
#             for form in formset:
#                 if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
#                     availability = form.save(commit=False)
#                     availability.service = service  # Link to service
#                     availability.save()

#             return redirect('services')  # Redirect to services page

#     else:
#         service_form = ServiceForm()
#         formset = ServiceAvailabilityFormSet(queryset=ServiceAvailability.objects.none())  # Empty formset

#     return render(request, 'accounts/add_service.html', {
#         'service_form': service_form,
#         'formset': formset
#     })




# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Booking, ServiceAvailability, User

# def get_available_slots(request, artist_id):
#     selected_date = request.GET.get("date")
#     artist = get_object_or_404(User, id=artist_id)

#     if not selected_date:
#         return JsonResponse({"error": "Invalid date selected"}, status=400)

#     # ✅ Get all booked slots for this artist and date
#     booked_slots = Booking.objects.filter(artist=artist, date=selected_date).values_list("time", flat=True)

#     # ✅ Get only the available time slots set by the artist for this date
#     available_slots = ServiceAvailability.objects.filter(
#         service__artist=artist, available_date=selected_date
#     ).values_list("available_time", flat=True)

#     # ✅ Convert to a list of time strings
#     booked_times = [time.strftime("%H:%M") for time in booked_slots]
#     artist_defined_times = [time.strftime("%H:%M") for time in available_slots]

#     # ✅ Show only available slots that are not booked
#     final_slots = [time for time in artist_defined_times if time not in booked_times]

#     return JsonResponse({"available_times": final_slots})




# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import ServiceAvailability, Service

# def get_available_dates(request, artist_id):
#     """ ✅ Fetch only available dates for the selected service """
#     service_id = request.GET.get("service_id")  # ✅ Get selected service ID

#     if not service_id:
#         return JsonResponse({"error": "Service ID is required"}, status=400)

#     service = get_object_or_404(Service, id=service_id, artist_id=artist_id)  # ✅ Ensure the service belongs to the artist

#     # ✅ Get unique available dates for the selected service
#     available_dates = ServiceAvailability.objects.filter(service=service).values_list("available_date", flat=True).distinct()

#     # ✅ Convert dates to string format (YYYY-MM-DD) for JavaScript
#     available_dates = [date.strftime("%Y-%m-%d") for date in available_dates]

#     return JsonResponse({"available_dates": available_dates})

from django.http import JsonResponse
from datetime import timedelta, datetime
from .models import Service

def get_available_dates(request, artist_id):
    service_id = request.GET.get('service_id')
    if service_id:
        service = Service.objects.get(id=service_id, artist_id=artist_id)
        work_days = service.work_days  # List of work days (e.g., ['Monday', 'Wednesday'])
        created_at = service.created_at  # Service creation date

        # Get today's date and calculate the available days starting from service's created_at
        available_dates = []
        current_date = created_at.date()

        # Loop through the next 30 days (or any reasonable range)
        for i in range(30):  # You can change this number as needed
            next_date = current_date + timedelta(days=i)
            # Check if the next_date is in the work_days list
            if next_date.strftime('%A') in work_days:
                available_dates.append(next_date.strftime('%Y-%m-%d'))  # Format it as 'YYYY-MM-DD'

        return JsonResponse({'available_dates': available_dates})
    return JsonResponse({'error': 'Service not found'}, status=400)

from django.http import JsonResponse
from datetime import datetime
# from .models import ServiceSchedule

def get_available_times(request, artist_id):
    service_id = request.GET.get('service_id')
    date = request.GET.get('date')  # Format 'YYYY-MM-DD'

    # Get weekday from date
    weekday = datetime.strptime(date, '%Y-%m-%d').strftime('%A')

    # Get the service schedules for the specific weekday and service
    service_schedules = ServiceSchedule.objects.filter(
        service_id=service_id,
        weekday=weekday  # Ensure the weekday matches the selected date
    )
    
    available_times = []
    for schedule in service_schedules:
        available_times.append(f"{schedule.start_time} - {schedule.end_time}")

    return JsonResponse({'available_times': available_times})






# from django.shortcuts import render
# from .models import User  # Assuming User model is used for artists

# def artist_list(request):
#     artists = User.objects.filter(is_artist=True)  # ✅ Only show users who are artists
#     cities = User.objects.filter(is_artist=True).values_list('city', flat=True).distinct()  # ✅ Get cities for artists only
#     return render(request, "accounts/artist_list.html", {"artists": artists, "cities": cities})







from django.shortcuts import render, get_object_or_404
from .models import User, Work

def artist_detail(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    works = Work.objects.filter(artist=artist)  # ✅ Fetch works related to the artist

    return render(request, 'accounts/artist_detail.html', {
        'artist': artist,
        'works': works
    })



# from django.shortcuts import render
# from .models import User, Service  # Ensure Service model exists

# def artist_list(request):
#     # ✅ Fetch all artists with services
#     artists = User.objects.filter(is_artist=True).prefetch_related('services')

#     # ✅ Get distinct cities for filtering
#     cities = artists.values_list('city', flat=True).distinct()

#     # ✅ Extract unique prices from services
#     prices = list(Service.objects.filter(artist__in=artists).values_list('price', flat=True))

#     price_ranges = []
    
#     if prices:
#         min_price = min(prices)
#         max_price = max(prices)

#         # ✅ Dynamically set step based on price spread
#         price_spread = max_price - min_price
#         if price_spread <= 1000:
#             step = 500  # Smaller spread → Smaller steps
#         elif price_spread <= 5000:
#             step = 1000  # Medium spread → Medium steps
#         else:
#             step = 2000  # Large spread → Wider steps

#         # ✅ Generate price ranges
#         start = min_price
#         while start < max_price:
#             end = start + step
#             if end >= max_price:
#                 price_ranges.append(f"{start}+")
#                 break
#             else:
#                 price_ranges.append(f"{start}-{end}")
#             start = end

#     return render(request, "accounts/artist_list.html", {
#         "artists": artists,
#         "cities": cities,
#         "price_ranges": price_ranges,  # ✅ Smarter ranges
#     })



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage

@login_required
def certificates_page(request):
    user = request.user  # Get the logged-in user

    if request.method == "POST" and request.FILES.get("training_certificate"):
        user.training_certificate = request.FILES["training_certificate"]
        user.save()
        return redirect("certificates")

    return render(request, "accounts/certificates.html", {"user": user})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Booking, Service
from django.http import JsonResponse







from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import User, Service, ServiceAvailability, Booking

  
# import json
# import logging
# from datetime import datetime
# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from django.core.mail import EmailMultiAlternatives
# from django.template.loader import render_to_string
# from django.utils.html import strip_tags
# from django.conf import settings
# from .models import Booking, Service, User, WorkingTime

# logger = logging.getLogger(__name__)

# # ✅ Map day names to Django week_day numbers (Sunday = 1, Monday = 2, ..., Saturday = 7)
# DAY_TO_WEEKDAY = {
#     "Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4,
#     "Thursday": 5, "Friday": 6, "Saturday": 7
# }

# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id)
#     services = Service.objects.filter(artist=artist)

#     # ✅ Prepare service data with correct workdays and schedules
#     service_data = []
#     for service in services:
#         work_days = service.work_days.all()
#         work_days_list = [work_day.day for work_day in work_days]

#         # ✅ Generate schedules and remove already booked slots
#         schedules = {}
#         for work_day in work_days:
#             all_slots = service.generate_slots_for_day(work_day)  # Generate slots
#             weekday_number = DAY_TO_WEEKDAY.get(work_day.day)  # Convert "Monday" to 2

#             # ✅ Get all booked slots for this **artist**, regardless of service
#             booked_slots = Booking.objects.filter(
#                 artist=artist,
#                 date__week_day=weekday_number  # ✅ Filter bookings for that weekday
#             ).values_list("start_time", "end_time")

#             # ✅ Convert booked slots into "HH:MM - HH:MM" format
#             booked_slots_formatted = [
#                 f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
#                 for start_time, end_time in booked_slots
#             ]

#             # ✅ Remove booked slots from available slots for all services
#             available_slots = [slot for slot in all_slots if slot not in booked_slots_formatted]
#             schedules[work_day.day] = available_slots  # ✅ Store only available slots

#         service_data.append({
#             "id": service.id,
#             "service_name": service.service_name,
#             "price": float(service.price),
#             "description": service.description,
#             "duration": service.get_total_duration_hms(),
#             "work_days": ",".join(work_days_list),
#             "schedules": schedules,
#         })

#     if request.method == "POST":
#         try:
#             print("🔍 Booking request received!")
#             print("📥 Received POST Data:", request.POST)

#             service_id = request.POST.get("service")
#             date_str = request.POST.get("date")
#             selected_schedule = request.POST.get("schedule")
#             latitude = request.POST.get("latitude")
#             longitude = request.POST.get("longitude")
#             payment_method = request.POST.get("payment_method")

#             if not service_id or not date_str or not selected_schedule:
#                 return JsonResponse({"error": "Missing required fields!"}, status=400)

#             service = get_object_or_404(Service, id=service_id, artist=artist)

#             # ✅ Convert date
#             try:
#                 date = datetime.strptime(date_str, "%Y-%m-%d").date()
#             except ValueError:
#                 return JsonResponse({"error": "Invalid date format!"}, status=400)

#             print(f"✅ Booking for {date} at {selected_schedule}")

#             # ✅ Validate if the selected schedule is available
#             work_day = service.work_days.filter(day=date.strftime("%A")).first()
#             if not work_day:
#                 return JsonResponse({"error": f"Service is not available on {date.strftime('%A')}."}, status=400)

#             available_slots = service.generate_slots_for_day(work_day)
#             if selected_schedule not in available_slots:
#                 return JsonResponse({"error": "Selected time slot is unavailable. Please choose a different slot."}, status=400)

#             # ✅ Extract and format start_time and end_time
#             start_time, end_time = selected_schedule.split("-")
#             start_time = start_time.strip()
#             end_time = end_time.strip()
#             start_time = datetime.strptime(start_time, "%H:%M").time()
#             end_time = datetime.strptime(end_time, "%H:%M").time()

#             # ✅ Double-check for overlapping bookings (in case of simultaneous submissions)
#             if Booking.objects.filter(
#                 artist=artist, date=date, 
#                 start_time=start_time, end_time=end_time
#             ).exists():
#                 return JsonResponse({"error": "This time slot is already booked. Please select another."}, status=400)

#             # ✅ Save booking
#             booking = Booking.objects.create(
#                 artist=artist,
#                 client=request.user,
#                 service=service,
#                 date=date,
#                 start_time=start_time,
#                 end_time=end_time,
#                 latitude=latitude if latitude else None,
#                 longitude=longitude if longitude else None,
#                 payment_method=payment_method,
#             )

#             print("✅ Booking successfully created!")

#             # ✅ Send confirmation email
#             subject = "Your Booking is Confirmed"
#             html_message = render_to_string("emails/booking_confirmation.html", {
#                 "user": request.user,
#                 "artist": artist,
#                 "service": service,
#                 "date": date.strftime("%A, %B %d, %Y"),
#                 "time_slot": selected_schedule,
#                 "payment_method": payment_method,
#             })

#             plain_message = strip_tags(html_message)
#             from_email = settings.DEFAULT_FROM_EMAIL
#             recipient_list = [request.user.email]

#             try:
#                 email = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
#                 email.attach_alternative(html_message, "text/html")
#                 email.send()
#             except Exception as e:
#                 print(f"❌ Email sending failed: {e}")

#             return JsonResponse({"success": "Booking successfully created! You will receive a confirmation email soon."}, status=200)

#         except Exception as e:
#             print(f"❌ Unexpected Error: {e}")  
#             return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

#     return render(request, "accounts/book_artist.html", {
#         "artist": artist,
#         "services": json.dumps(service_data)
#     })


from django.shortcuts import render
from .models import Booking

def bookings(request):
    user = request.user

    # ✅ Show bookings for the logged-in user (either client or artist)
    if user.is_artist:
        user_bookings = Booking.objects.filter(artist=user)
    else:
        user_bookings = Booking.objects.filter(client=user)

    return render(request, 'accounts/bookings.html', {'user_bookings': user_bookings})



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.decorators import login_required
from .models import Booking
import logging

logger = logging.getLogger(__name__)






# from django.shortcuts import get_object_or_404, redirect
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
# from django.core.mail import send_mail
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Booking

# @login_required
# @csrf_exempt
# def update_booking_status(request, booking_id):
#     """ Allows an artist to confirm or cancel a booking and send email notifications. """
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             new_status = data.get("status")
#             booking = get_object_or_404(Booking, id=booking_id)

#             # ✅ Ensure only the assigned artist can update the booking
#             if request.user != booking.artist:
#                 return JsonResponse({"success": False, "error": "Only the assigned artist can update this booking."}, status=403)

#             # ✅ Update the booking status
#             booking.status = new_status
#             booking.save()

#             # ✅ Construct email details
#             subject = f"Booking {new_status}: {booking.service.service_name}"
#             message = f"""
#                 Hello {booking.client.first_name},

#                 Your booking for {booking.service.service_name} with {booking.artist.first_name} {booking.artist.last_name} has been {new_status.lower()}.

#                 Booking Details:
#                 - Service: {booking.service.service_name}
#                 - Artist: {booking.artist.first_name} {booking.artist.last_name}
#                 - Date: {booking.date}
#                 - Time: {booking.time}
#                 - Payment Method: {booking.payment_method}
#                 - Price: ${booking.service.price}

#                 If you have any questions, please contact the artist at {booking.artist.email}.

#                 Best regards,
#                 Artist Finder Team
#             """

#             # ✅ Send email to client
#             send_mail(
#                 subject,
#                 message,
#                 "no-reply@artistfinder.com",
#                 [booking.client.email],
#                 fail_silently=False,
#             )

#             # ✅ Send email to artist as well
#             send_mail(
#                 f"Booking {new_status} - {booking.client.first_name}",
#                 f"Hello {booking.artist.first_name},\n\nYou have {new_status.lower()} a booking.\n\n{message}",
#                 "no-reply@artistfinder.com",
#                 [booking.artist.email],
#                 fail_silently=False,
#             )

#             return JsonResponse({
#                 "success": True,
#                 "message": f"Booking has been {new_status.lower()}!",
#                 "status": booking.status
#             })

#         except Booking.DoesNotExist:
#             return JsonResponse({"success": False, "error": "Booking not found"}, status=404)

#         except json.JSONDecodeError:
#             return JsonResponse({"success": False, "error": "Invalid JSON request"}, status=400)

#     return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)

# import json
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
# from .models import Booking

# @csrf_exempt  # ✅ Allow AJAX requests
# def update_booking_status(request, booking_id):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             new_status = data.get("status", "").lower()

#             if new_status not in ["confirmed", "cancelled"]:
#                 return JsonResponse({"error": "Invalid status update"}, status=400)

#             booking = get_object_or_404(Booking, id=booking_id)
#             booking.status = new_status.capitalize()
#             booking.save()

#             # ✅ Send notification email (if needed)
#             if new_status == "confirmed":
#                 send_confirmation_email(booking)
#             elif new_status == "cancelled":
#                 send_cancellation_email(booking)

#             return JsonResponse({"success": f"Booking {new_status} successfully!"})
#         except Exception as e:
#             return JsonResponse({"error": f"Error updating booking: {str(e)}"}, status=500)

#     return JsonResponse({"error": "Invalid request"}, status=400)

# def send_confirmation_email(booking):
#     """Send an email when the booking is confirmed."""
#     subject = "Your Booking is Confirmed!"
#     message = f"""
#     Hello {booking.client.first_name},

#     Your booking for {booking.service.service_name} with {booking.artist.first_name} {booking.artist.last_name} has been confirmed.

#     📌 Booking Details:
#     - Date: {booking.date.strftime('%A, %B %d, %Y')}
#     - Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
#     - Payment Method: {booking.payment_method}

#     Thank you for using our platform!

#     Regards,
#     ArtistFinder Team
#     """
#     booking.client.email_user(subject, message)

# def send_cancellation_email(booking):
#     """Send an email when the booking is cancelled."""
#     subject = "Your Booking Has Been Cancelled"
#     message = f"""
#     Hello {booking.client.first_name},

#     Unfortunately, your booking for {booking.service.service_name} with {booking.artist.first_name} {booking.artist.last_name} has been cancelled.

#     If you have any questions, please contact support.

#     Regards,
#     ArtistFinder Team
#     """
#     booking.client.email_user(subject, message) aaja



import json
import os
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Booking

@csrf_exempt  # ✅ Allow AJAX requests
def update_booking_status(request, booking_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_status = data.get("status", "").lower()

            if new_status not in ["confirmed", "cancelled"]:
                return JsonResponse({"error": "Invalid status update"}, status=400)

            booking = get_object_or_404(Booking, id=booking_id)
            booking.status = new_status.capitalize()
            booking.save()

            # ✅ Send notification email
            if new_status == "confirmed":
                send_confirmation_email(booking)
            elif new_status == "cancelled":
                send_cancellation_email(booking)

            return JsonResponse({"success": f"Booking {new_status} successfully!"})
        except Exception as e:
            return JsonResponse({"error": f"Error updating booking: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

def send_confirmation_email(booking):
    """Send a **custom HTML email** when the booking is confirmed."""
    subject = "🎉 Your Booking is Confirmed!"
    html_message = render_to_string("emails/booking_confirmation2.html", {
        "user": booking.client,
        "artist": booking.artist,
        "service": booking.service,
        "date": booking.date.strftime("%A, %B %d, %Y"),
        "start_time": booking.start_time.strftime("%I:%M %p"),
        "end_time": booking.end_time.strftime("%I:%M %p"),
        "payment_method": booking.payment_method,
        "booking_history_url": f"{settings.SITE_URL}/booking-history/",
        "support_url": f"{settings.SITE_URL}/support/",
    })
    
    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [booking.client.email]

    try:
        email = EmailMessage(subject, html_message, from_email, recipient_list)
        email.content_subtype = "html"

        # Attach logo
        logo_path = os.path.join(settings.BASE_DIR, "static/images/logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo:
                email.attach("logo.png", logo.read(), "image/png")

        email.send()
        print("📧 Booking confirmation email sent successfully!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

def send_cancellation_email(booking):
    """Send a **custom HTML email** when the booking is cancelled."""
    subject = "❌ Your Booking Has Been Cancelled"
    html_message = render_to_string("emails/booking_cancellation.html", {
        "user": booking.client,
        "artist": booking.artist,
        "service": booking.service,
        "date": booking.date.strftime("%A, %B %d, %Y"),
        "start_time": booking.start_time.strftime("%I:%M %p"),
        "end_time": booking.end_time.strftime("%I:%M %p"),
        "support_url": f"{settings.SITE_URL}/support/",
    })

    plain_message = strip_tags(html_message)
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [booking.client.email]

    try:
        email = EmailMessage(subject, html_message, from_email, recipient_list)
        email.content_subtype = "html"

        # Attach logo
        logo_path = os.path.join(settings.BASE_DIR, "static/images/logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo:
                email.attach("logo.png", logo.read(), "image/png")

        email.send()
        print("📧 Booking cancellation email sent successfully!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")



# from datetime import datetime
# from django.utils.timezone import now, make_aware
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from .models import Booking

# @login_required(login_url='login')
# def booking_history(request):
#     user = request.user
#     today = now().date()

#     user_bookings = Booking.objects.filter(client=user).order_by('-date')

#     # Calculate the remaining time for cancellation
#     for booking in user_bookings:
#         appointment_datetime = make_aware(datetime.combine(booking.date, booking.time))  # Convert to timezone-aware
#         remaining_time = (appointment_datetime - now()).total_seconds() / 3600  # Convert to hours
#         booking.time_left = remaining_time  # Attach to object for template use

#     return render(request, "accounts/booking_history.html", {
#         "user_bookings": user_bookings,
#         "today": today,  # Pass today's date for comparison
#     })
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booking
from datetime import datetime, timedelta

@login_required
def booking_history(request):
    user_bookings = Booking.objects.filter(client=request.user).order_by('-date', '-start_time')

    for booking in user_bookings:
        booking_datetime = datetime.combine(booking.date, booking.start_time)

        # ✅ Ensure end_time is correctly calculated (including travel time)
        if not booking.end_time and booking.service:
            duration_minutes = int(booking.service.duration.total_seconds() / 60)
            travel_time_minutes = int(booking.service.travel_time.total_seconds() / 60)
            
            total_minutes = duration_minutes + travel_time_minutes
            end_datetime = booking_datetime + timedelta(minutes=total_minutes)
            booking.end_time = end_datetime.time()

        # ✅ Format duration in HH:MM:SS format
        if booking.service and booking.service.total_duration:
            total_seconds = int(booking.service.total_duration.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            booking.formatted_duration = f"{hours:02}:{minutes:02}:{seconds:02}"  # Fix format

        # ✅ Ensure time left for cancellation (24-hour rule)
        now_time = datetime.now()
        time_left = (booking_datetime - now_time).total_seconds() / 3600
        booking.time_left = max(0, round(time_left))  # Prevent negative values

    return render(request, 'accounts/booking_history.html', {'user_bookings': user_bookings})


from django.shortcuts import render
from .models import AboutUs

def aboutus(request):
    about = AboutUs.objects.first()  # ✅ Get the first About Us entry
    return render(request, "accounts/aboutus.html", {"about": about})
from django.shortcuts import render
from django.http import JsonResponse
from .models import ContactUsPage, ContactMessage

def contact_us(request):
    contact_page = ContactUsPage.objects.first()

    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        ContactMessage.objects.create(name=name, email=email, subject=subject, message=message)

        return JsonResponse({"success": True})  # ✅ Return JSON response

    return render(request, "accounts/contactus.html", {"contact_page": contact_page})





from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }








# @login_required
# def add_review(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)

#     # ✅ Get only services booked by the user for this artist
#     booked_services = Service.objects.filter(
#         booking__client=request.user, booking__artist=artist, booking__status="Confirmed"
#     ).distinct()

#     if not booked_services.exists():
#         messages.error(request, "You can only review services you've booked and confirmed.")
#         return redirect('home')

#     if request.method == "POST":
#         form = ReviewForm(request.POST)
#         service_id = request.POST.get("service")  # ✅ Get the service ID from the form

#         if not service_id:
#             messages.error(request, "Please select a valid service.")
#             return redirect(request.path)

#         service = get_object_or_404(Service, id=service_id)

#         if service not in booked_services:  # ✅ Ensure the service is valid
#             messages.error(request, "You can only review services you have booked.")
#             return redirect(request.path)

#         if form.is_valid():
#             review = form.save(commit=False)
#             review.artist = artist
#             review.user = request.user
#             review.service = service  # ✅ Assign the valid service
#             review.is_anonymous = request.POST.get("anonymous") == "on"
#             review.save()
#             messages.success(request, "Your review has been submitted successfully!")
#             return redirect('home')
#     else:
#         form = ReviewForm()

#     return render(request, 'accounts/review_form.html', {
#         'form': form,
#         'artist': artist,
#         'services': booked_services
#     })
@login_required
def add_review(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)

    # ✅ Only fetch services with COMPLETED bookings
    booked_services = Service.objects.filter(
        booking__client=request.user, 
        booking__artist=artist, 
        booking__status="Completed"
    ).distinct()

    if not booked_services.exists():
        messages.error(request, "You can only review services you've completed.")
        return redirect('home')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        service_id = request.POST.get("service")

        if not service_id:
            messages.error(request, "Please select a valid service.")
            return redirect(request.path)

        service = get_object_or_404(Service, id=service_id)

        # ✅ Verify the service is among the user's COMPLETED services
        if service not in booked_services:
            messages.error(request, "You can only review services you've completed.")
            return redirect(request.path)

        if form.is_valid():
            review = form.save(commit=False)
            review.artist = artist
            review.user = request.user
            review.service = service
            review.is_anonymous = request.POST.get("anonymous") == "on"
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('home')
    else:
        form = ReviewForm()

    return render(request, 'accounts/review_form.html', {
        'form': form,
        'artist': artist,
        'services': booked_services
    })



def create_booking(request):
    if request.method == "POST":
        service = request.POST.get("service")
        user = request.user
        Booking.objects.create(user=user, service=service, is_new=True)  # ✅ Mark as new
        return JsonResponse({'status': 'success'})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import User, Review, Booking

@login_required(login_url='login')
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # ✅ Ensure only the user who created the review can delete it
    if request.user == review.user:
        review.delete()
    return redirect('home')  # ✅ Redirect back to home after deletion


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Work

@login_required
def delete_work(request, work_id):
    work = get_object_or_404(Work, id=work_id, artist=request.user)

    if request.method == "POST":
        work.delete()
        messages.success(request, "Work deleted successfully!")
        return redirect('artist_dashboard')

    return redirect('artist_dashboard')


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service

@login_required
def delete_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # ✅ Ensure only the owner can delete
    if request.user != service.artist:
        messages.error(request, "You can only delete your own services.")
        return redirect("services")

    service.delete()
    messages.success(request, "Service deleted successfully.")
    return redirect("services")






from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Service

@login_required
def availability_status(request):
    services = Service.objects.filter(artist=request.user)  # ✅ Get services of logged-in artist
    return render(request, "accounts/availability_status.html", {"services": services})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

@login_required
def availability_status(request):
    if not request.user.is_artist:
        messages.error(request, "Only artists can update availability.")
        return redirect("home")  # Redirect if not an artist

    return render(request, "accounts/availability_status.html")

@login_required
def toggle_availability(request):
    if request.user.is_artist:
        request.user.is_available = not request.user.is_available  # ✅ Toggle availability status
        request.user.save()
        messages.success(request, f"Availability updated to {'Available' if request.user.is_available else 'Not Available'}!")
    return redirect("availability_status")  



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Work
from django.conf import settings
import requests

from .forms import WorkUploadForm  # ✅ Ensure the form is imported

@login_required(login_url='artist_login')
def update_work(request, work_id):
    work = get_object_or_404(Work, id=work_id, artist=request.user)

    if request.method == "POST":
        form = WorkUploadForm(request.POST, request.FILES, instance=work)
        if form.is_valid():
            form.save()
            messages.success(request, "Work updated successfully!")
            return redirect("artist_dashboard")
    else:
        form = WorkUploadForm(instance=work)

    return render(request, "accounts/update_work.html", {"form": form, "work": work})




from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

@login_required
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.city = request.POST.get("city", user.city)
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')

        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('user_profile')  # Redirect back to profile page

    return render(request, 'accounts/user_profile.html', {'user': user})



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User

@login_required(login_url='artist_login')
def artist_profile(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone = request.POST.get('phone')
        user.city = request.POST.get('city')
        user.works_at = request.POST.get('works_at')
        user.experience_years = request.POST.get('experience_years')

        if 'profile_image' in request.FILES:
            user.profile_image = request.FILES['profile_image']

        user.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('artist_profile')

    return render(request, 'accounts/artist_profile.html')


  


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewForm

@login_required
def edit_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review updated successfully!")
            return redirect("home")  # Redirect to homepage or artist details

    else:
        form = ReviewForm(instance=review)

    return render(request, "accounts/edit_review.html", {"form": form, "review": review})




from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from .forms import ReviewReplyForm

@login_required
def reply_to_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    # ✅ Ensure only the artist who owns the service can reply
    if request.user != review.artist:
        messages.error(request, "You can only reply to reviews on your own services.")
        return redirect("services")

    if request.method == "POST":
        form = ReviewReplyForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Reply posted successfully!")
            return redirect("services")

    else:
        form = ReviewReplyForm(instance=review)

    return render(request, "accounts/reply_review.html", {"form": form, "review": review})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Review

@login_required
def edit_review_reply(request, review_id):
    """ ✅ Allow artists to edit their own review replies """
    review = get_object_or_404(Review, id=review_id)

    # ✅ Ensure only the artist can edit their reply
    if request.user != review.artist:
        return JsonResponse({"success": False, "message": "You can only edit your own replies."}, status=403)

    if request.method == "POST":
        new_reply = request.POST.get("artist_reply")
        review.artist_reply = new_reply
        review.save()
        messages.success(request, "Your reply has been updated.")
        return redirect("services")  # ✅ Redirect to services page

    return render(request, "accounts/edit_review_reply.html", {"review": review})


@login_required
def delete_review_reply(request, review_id):
    """ ✅ Allow artists to delete their review reply """
    review = get_object_or_404(Review, id=review_id)

    # ✅ Ensure only the artist can delete their own reply
    if request.user != review.artist:
        return JsonResponse({"success": False, "message": "You can only delete your own replies."}, status=403)

    review.artist_reply = ""  # ✅ Remove the reply
    review.save()
    messages.success(request, "Your reply has been deleted.")
    return redirect("services")  # ✅ Redirect back to services

from django.shortcuts import render

def customize_booking(request):
    return render(request, 'accounts/customize_booking.html')


from django.shortcuts import render, redirect
from django.http import HttpResponse

def process_booking(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        time = request.POST.get('time')
        members = request.POST.get('members')
        services = request.POST.getlist('services')  # ✅ Get multiple selected services
        details = request.POST.get('details')

        services_str = ", ".join(services)  # Convert list to string

        # ✅ Save the booking to the database (optional)
        print(f"Booking Received - Date: {date}, Time: {time}, Members: {members}, Services: {services_str}, Details: {details}")

        return HttpResponse(f"Booking confirmed for {members} members on {date} at {time} for {services_str}!")

    return redirect('customize_booking')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import TrainingCertificate
from .forms import TrainingCertificateForm  # ✅ Make sure this import exists


def artist_certificates(request):
    if request.method == "POST":
        form = TrainingCertificateForm(request.POST, request.FILES)
        if form.is_valid():
            certificate = form.save(commit=False)
            certificate.artist = request.user  # ✅ Associate with logged-in artist
            certificate.save()
            messages.success(request, "Certificate uploaded successfully!")
            return redirect("artist_certificates")

    certificates = request.user.certificates.all()
    return render(request, "accounts/certificates.html", {"certificates": certificates})

# ✅ Edit Certificate
def edit_certificate(request, certificate_id):
    certificate = get_object_or_404(TrainingCertificate, id=certificate_id, artist=request.user)

    if request.method == "POST":
        form = TrainingCertificateForm(request.POST, request.FILES, instance=certificate)
        if form.is_valid():
            form.save()
            messages.success(request, "Certificate updated successfully!")
            return redirect("artist_certificates")

    return render(request, "accounts/edit_certificate.html", {"form": TrainingCertificateForm(instance=certificate)})

# ✅ Delete Certificate
def delete_certificate(request, certificate_id):
    certificate = get_object_or_404(TrainingCertificate, id=certificate_id, artist=request.user)

    if request.method == "POST":
        certificate.delete()
        messages.success(request, "Certificate deleted successfully!")
        return redirect("artist_certificates")

    return render(request, "delete_certificate.html", {"certificate": certificate})


from django.shortcuts import render

def booking_location(request):
    return render(request, 'accounts/booking_location.html')
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import WeekSchedule
from .forms import WeekScheduleForm

@login_required
def week_schedule_view(request):
    if request.method == 'POST':
        form = WeekScheduleForm(request.POST)
        if form.is_valid():
            week_schedule = form.save(commit=False)
            week_schedule.artist = request.user
            week_schedule.save()
            return redirect('services')  # Redirect back to services page
    else:
        form = WeekScheduleForm()

    schedules = WeekSchedule.objects.filter(artist=request.user)
    
    return render(request, 'accounts/week_schedule.html', {'form': form, 'schedules': schedules})



from django.shortcuts import render, redirect
from .models import Service, WorkingTime
from .forms import ServiceForm

def add_service(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.artist = request.user  # ✅ Assign the logged-in artist
            service.save()
            form.save_m2m()  # ✅ Save ManyToManyField
            return redirect('services')  # ✅ Redirect to services list
    else:
        form = ServiceForm()

    return render(request, "accounts/add_service.html", {"form": form})









from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
# from .models import ServiceSchedule

def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(ServiceSchedule, id=schedule_id)
    schedule.delete()
    messages.success(request, "Schedule removed successfully!")
    return redirect('service_schedule')





from django.http import JsonResponse
from .models import Booking

def get_notifications(request):
    new_bookings = Booking.objects.filter(is_new=True).count()  # Fetch count of new bookings
    
    return JsonResponse({'new_bookings': new_bookings})



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def mark_notifications_read(request):
    Booking.objects.filter(is_new=True).update(is_new=False)  # Mark as seen
    return JsonResponse({'status': 'success'})


from django.shortcuts import render, redirect
from .models import WorkingTime
from .forms import WorkingTimeForm

def working_time_view(request):
    if request.method == "POST":
        form = WorkingTimeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('working_time')  # Refresh the page after adding
    else:
        form = WorkingTimeForm()

    working_times = WorkingTime.objects.all()  # Fetch all working times

    return render(request, 'accounts/working_time.html', {'form': form, 'working_times': working_times})
from django.shortcuts import get_object_or_404

def delete_working_time(request, time_id):
    time_entry = get_object_or_404(WorkingTime, id=time_id)
    time_entry.delete()
    return redirect('working_time')


from django.http import JsonResponse
from .models import Service

def get_service_workdays(request, service_id):
    """ Fetches available workdays for a selected service. """
    try:
        service = Service.objects.get(id=service_id)
        workdays = list(service.work_days)  # Convert MultiSelectField to list
        return JsonResponse({"workdays": workdays})
    except Service.DoesNotExist:
        return JsonResponse({"error": "Service not found"}, status=404)


# import json
# import requests
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings
# from .models import Service, User
# from datetime import datetime

# @csrf_exempt
# def initiate_khalti_payment(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request method!"}, status=400)

#     try:
#         data = json.loads(request.body)
#         service_id = data.get("service_id")
#         artist_id = data.get("artist_id")
#         date = data.get("date")
#         schedule = data.get("schedule")
#         latitude = data.get("latitude")
#         longitude = data.get("longitude")

#         if not all([service_id, artist_id, date, schedule]):
#             return JsonResponse({"error": "Missing required fields!"}, status=400)

#         service = get_object_or_404(Service, id=service_id)
#         artist = get_object_or_404(User, id=artist_id, is_artist=True)
#         user = request.user  # 🔥 Get the logged-in client

#         # ✅ Convert price to paisa (Nepali currency)
#         amount = int(service.price * 100)
#         purchase_order_id = f"order_{datetime.now().timestamp()}"
#         purchase_order_name = f"Booking {service.service_name}"

#         payload = {
#             "return_url": settings.KHALTI_RETURN_URL,
#             "website_url": settings.SITE_URL,
#             "amount": amount,
#             "purchase_order_id": purchase_order_id,
#             "purchase_order_name": purchase_order_name,
#             "customer_info": {
#                 "name": user.get_full_name(),
#                 "email": user.email,
#                 "phone": user.phone,
#             },
#         }

#         headers = {
#             "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }

#         response = requests.post(f"{settings.KHALTI_API_URL}epayment/initiate/", json=payload, headers=headers)
#         response_data = response.json()

#         if response.status_code == 200 and "pidx" in response_data:
#             # ✅ Store booking data in session (including client_id)
#             # ✅ Split the schedule string into start_time and end_time
#             start_time, end_time = schedule.split(" - ")

#             request.session["pending_booking"] = {
#                 "client_id": user.id,
#                 "service_id": service.id,
#                 "artist_id": artist.id,
#                 "date": date,
#                 "start_time": start_time.strip(),  # ✅ Save start_time
#                 "end_time": end_time.strip(),      # ✅ Save end_time
#                 "latitude": latitude,
#                 "longitude": longitude,
#                 "payment_method": "Khalti",
#                 "transaction_id": response_data["pidx"]
#             }


#             print("📌 SESSION DATA AFTER FIX:", request.session["pending_booking"])  # Debugging print

#             return JsonResponse({"success": True, "payment_url": response_data["payment_url"], "pidx": response_data["pidx"]})

#         else:
#             return JsonResponse({"error": "Failed to initiate payment!", "details": response_data}, status=400)

#     except Exception as e:
#         return JsonResponse({"error": f"Error initiating payment: {str(e)}"}, status=500)

# @csrf_exempt
# def verify_khalti_payment(request):
#     if request.method == "POST":
#         pidx = request.POST.get("pidx")

#         if not pidx:
#             return JsonResponse({"error": "Invalid Payment ID!"}, status=400)

#         # ✅ Send request to Khalti API for payment verification
#         payload = {"pidx": pidx}
#         headers = {
#             "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }
#         response = requests.post(f"{settings.KHALTI_API_URL}epayment/lookup/", json=payload, headers=headers)
#         response_data = response.json()

#         # ✅ Debugging: Print session data before saving booking
#         print("📌 SESSION DATA BEFORE SAVING BOOKING:", request.session.get("pending_booking"))

#         if response_data.get("status") == "Completed":
#             pending_booking = request.session.get("pending_booking")

#             if not pending_booking or "client_id" not in pending_booking:
#                 return JsonResponse({"error": "No client ID found in booking data!"}, status=400)

#             try:
#                 # ✅ Retrieve all necessary booking details
#                 artist = get_object_or_404(User, id=pending_booking["artist_id"], is_artist=True)
#                 client = get_object_or_404(User, id=pending_booking["client_id"])  # 🔥 Ensure client_id is fetched
#                 service = get_object_or_404(Service, id=pending_booking["service_id"])
#                 date = datetime.strptime(pending_booking["date"], "%Y-%m-%d").date()

#                 start_time = datetime.strptime(pending_booking["start_time"], "%H:%M").time()
#                 end_time = datetime.strptime(pending_booking["end_time"], "%H:%M").time()

#                 # ✅ Save booking to the database
#                 booking = Booking.objects.create(
#                     artist=artist,
#                     client=client,
#                     service=service,
#                     date=date,
#                     start_time=start_time,
#                     end_time=end_time,
#                     latitude=pending_booking.get("latitude"),
#                     longitude=pending_booking.get("longitude"),
#                     payment_method="Khalti",
#                     status="Confirmed",
#                     transaction_id=pidx,
#                 )
#                 send_confirmation_email(booking)
#                 # ✅ Clear session after successful booking
#                 del request.session["pending_booking"]

#                 print(f"✅ Booking saved successfully: {booking}")
#                 return JsonResponse({"success": "Payment verified and booking confirmed!"})

#             except Exception as e:
#                 return JsonResponse({"error": f"Error saving booking: {str(e)}"}, status=500)

#         else:
#             return JsonResponse({"error": "Payment verification failed!", "details": response_data}, status=400)

#     return JsonResponse({"error": "Invalid request!"}, status=400)

import json
import requests
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.mail import send_mail
from .models import Service, User, Booking


def send_confirmation_email(booking):
    subject = "🎉 Booking Confirmed!"
    message = (
        f"Hi {booking.client.first_name},\n\n"
        f"Your booking with {booking.artist.get_full_name()} for {booking.service.service_name} "
        f"on {booking.date} at {booking.start_time} is confirmed!\n\nThank you for using our service!"
    )
    recipient_list = [booking.client.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


@csrf_exempt
def initiate_khalti_payment(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method!"}, status=400)

    try:
        data = json.loads(request.body)
        service_id = data.get("service_id")
        artist_id = data.get("artist_id")
        date = data.get("date")
        schedule = data.get("schedule")
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        if not all([service_id, artist_id, date, schedule]):
            return JsonResponse({"error": "Missing required fields!"}, status=400)

        service = get_object_or_404(Service, id=service_id)
        artist = get_object_or_404(User, id=artist_id, is_artist=True)
        user = request.user

        if not user.phone:
            return JsonResponse({"error": "Your phone number is required for Khalti payment."}, status=400)

        amount = int(service.price * 100)
        purchase_order_id = f"order_{datetime.now().timestamp()}"
        purchase_order_name = f"Booking {service.service_name}"

        payload = {
            "return_url": settings.KHALTI_RETURN_URL,
            "website_url": settings.SITE_URL,
            "amount": amount,
            "purchase_order_id": purchase_order_id,
            "purchase_order_name": purchase_order_name,
            "customer_info": {
                "name": user.get_full_name(),
                "email": user.email,
                "phone": user.phone,
            },
        }

        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        print("Initiating Payment to Khalti")
        print("Payload:", json.dumps(payload, indent=2))
        print("Headers:", headers)
        print("Endpoint:", f"{settings.KHALTI_API_URL}epayment/initiate/")

        response = requests.post(f"{settings.KHALTI_API_URL}epayment/initiate/", json=payload, headers=headers)

        try:
            response_data = response.json()
        except Exception as e:
            print("Invalid JSON response:", response.text)
            return JsonResponse({"error": "Invalid response from Khalti.", "raw": response.text}, status=400)

        if response.status_code == 200 and "pidx" in response_data:
            start_time, end_time = schedule.split(" - ")

            request.session["pending_booking"] = {
                "client_id": user.id,
                "service_id": service.id,
                "artist_id": artist.id,
                "date": date,
                "start_time": start_time.strip(),
                "end_time": end_time.strip(),
                "latitude": latitude,
                "longitude": longitude,
                "payment_method": "Khalti",
                "transaction_id": response_data["pidx"]
            }

            return JsonResponse({
                "success": True,
                "payment_url": response_data["payment_url"],
                "pidx": response_data["pidx"]
            })
        else:
            print("Failed Khalti Response:", response_data)
            return JsonResponse({"error": response_data.get("detail", "Failed to initiate wallet payment.")}, status=400)

    except Exception as e:
        print("Unexpected Error:", str(e).encode('utf-8', errors='replace').decode())
        return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)


# @csrf_exempt
# def verify_khalti_payment(request):
#     if request.method == "POST":
#         pidx = request.POST.get("pidx")

#         if not pidx:
#             return JsonResponse({"error": "Invalid Payment ID!"}, status=400)

#         payload = {"pidx": pidx}
#         headers = {
#             "Authorization": f"Key {settings.KHALTI_SECRET_KEY}",
#             "Content-Type": "application/json",
#         }

#         print("🔍 Verifying Payment at Khalti")
#         print("Payload:", payload)
#         print("Headers:", headers)

#         response = requests.post(f"{settings.KHALTI_API_URL}epayment/lookup/", json=payload, headers=headers)

#         try:
#             response_data = response.json()
#             print("📨 Khalti Verification Response:", response_data)
#         except Exception as e:
#             print("❌ JSON Decode Error:", response.text)
#             return JsonResponse({"error": "Invalid JSON from Khalti."}, status=400)

#         if response_data.get("status") == "Completed":
#             pending_booking = request.session.get("pending_booking")

#             if not pending_booking or "client_id" not in pending_booking:
#                 return JsonResponse({"error": "No client ID found in booking data!"}, status=400)

#             try:
#                 artist = get_object_or_404(User, id=pending_booking["artist_id"], is_artist=True)
#                 client = get_object_or_404(User, id=pending_booking["client_id"])
#                 service = get_object_or_404(Service, id=pending_booking["service_id"])

#                 date = datetime.strptime(pending_booking["date"], "%Y-%m-%d").date()
#                 start_time = datetime.strptime(pending_booking["start_time"], "%H:%M").time()
#                 end_time = datetime.strptime(pending_booking["end_time"], "%H:%M").time()

#                 booking = Booking.objects.create(
#                     artist=artist,
#                     client=client,
#                     service=service,
#                     date=date,
#                     start_time=start_time,
#                     end_time=end_time,
#                     latitude=pending_booking.get("latitude"),
#                     longitude=pending_booking.get("longitude"),
#                     payment_method="Khalti",
#                     status="Confirmed",
#                     transaction_id=transaction_id,
#                 )

#                 send_confirmation_email(booking)
#                 del request.session["pending_booking"]

#                 return JsonResponse({"success": "Payment verified and booking confirmed!"})

#             except Exception as e:
#                 return JsonResponse({"error": f"Error saving booking: {str(e)}"}, status=500)

#         else:
#             return JsonResponse({"error": "Payment verification failed!", "details": response_data}, status=400)

#     return JsonResponse({"error": "Invalid request!"}, status=400)

# from datetime import datetime
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.conf import settings
# from .models import Booking, Service, User
# from .utils import send_confirmation_email  # if you have a utility function for sending emails
# import requests
# import json

# @csrf_exempt
# def verify_khalti_payment(request):
#     if request.method == "POST":
#         pidx = request.POST.get("pidx")

#         if not pidx:
#             return JsonResponse({"error": "Invalid Payment ID!"}, status=400)

#         payload = {"pidx": pidx}
#         headers = {
#             "Authorization": f"Key {settings.KHALTI_SECRET_KEY.strip()}",
#             "Content-Type": "application/json",
#         }

#         print("🔍 Verifying Payment at Khalti")
#         print("Payload:", payload)
#         print("Headers:", headers)

#         response = requests.post(f"{settings.KHALTI_API_URL}epayment/lookup/", json=payload, headers=headers)

#         try:
#             response_data = response.json()
#             print("📨 Khalti Verification Response:", response_data)
#         except Exception as e:
#             print("❌ JSON Decode Error:", response.text)
#             return JsonResponse({"error": "Invalid JSON from Khalti."}, status=400)

#         if response_data.get("status") == "Completed":
#             pending_booking = request.session.get("pending_booking")

#             if not pending_booking or "client_id" not in pending_booking:
#                 return JsonResponse({"error": "No client ID found in booking data!"}, status=400)

#             try:
#                 artist = get_object_or_404(User, id=pending_booking["artist_id"], is_artist=True)
#                 client = get_object_or_404(User, id=pending_booking["client_id"])
#                 service = get_object_or_404(Service, id=pending_booking["service_id"])

#                 date = datetime.strptime(pending_booking["date"], "%Y-%m-%d").date()
#                 start_time = datetime.strptime(pending_booking["start_time"], "%H:%M").time()
#                 end_time = datetime.strptime(pending_booking["end_time"], "%H:%M").time()

#                 # ✅ Fetch actual transaction ID for refund support
#                 transaction_id = response_data.get("transaction_id")

#                 if not transaction_id:
#                     return JsonResponse({"error": "Transaction ID missing in response!"}, status=400)

#                 booking = Booking.objects.create(
#                     artist=artist,
#                     client=client,
#                     service=service,
#                     date=date,
#                     start_time=start_time,
#                     end_time=end_time,
#                     latitude=pending_booking.get("latitude"),
#                     longitude=pending_booking.get("longitude"),
#                     payment_method="Khalti",
#                     status="Confirmed",
#                     transaction_id=transaction_id,  # ✅ Save real transaction_id
#                 )

#                 send_confirmation_email(booking)
#                 del request.session["pending_booking"]

#                 return JsonResponse({"success": "Payment verified and booking confirmed!"})

#             except Exception as e:
#                 return JsonResponse({"error": f"Error saving booking: {str(e)}"}, status=500)

#         else:
#             return JsonResponse({"error": "Payment verification failed!", "details": response_data}, status=400)

#     return JsonResponse({"error": "Invalid request!"}, status=400)

# from datetime import datetime
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.conf import settings
# from .models import Booking, Service, User
# # from .utils import send_confirmation_email  # if you have a utility function for sending emails
# import requests
# import json

# @csrf_exempt
# def verify_khalti_payment(request):
#     if request.method == "POST":
#         pidx = request.POST.get("pidx")

#         if not pidx:
#             return JsonResponse({"error": "Invalid Payment ID!"}, status=400)

#         payload = {"pidx": pidx}
#         headers = {
#             "Authorization": f"Key {settings.KHALTI_SECRET_KEY.strip()}",
#             "Content-Type": "application/json",
#         }

#         print("🔍 Verifying Payment at Khalti")
#         print("Payload:", payload)
#         print("Headers:", headers)

#         response = requests.post(f"{settings.KHALTI_API_URL}epayment/lookup/", json=payload, headers=headers)

#         try:
#             response_data = response.json()
#             print("📨 Khalti Verification Response:", response_data)
#         except Exception as e:
#             print("❌ JSON Decode Error:", response.text)
#             return JsonResponse({"error": "Invalid JSON from Khalti."}, status=400)

#         if response_data.get("status") == "Completed":
#             pending_booking = request.session.get("pending_booking")

#             if not pending_booking or "client_id" not in pending_booking:
#                 return JsonResponse({"error": "No client ID found in booking data!"}, status=400)

#             try:
#                 artist = get_object_or_404(User, id=pending_booking["artist_id"], is_artist=True)
#                 client = get_object_or_404(User, id=pending_booking["client_id"])
#                 service = get_object_or_404(Service, id=pending_booking["service_id"])

#                 date = datetime.strptime(pending_booking["date"], "%Y-%m-%d").date()
#                 start_time = datetime.strptime(pending_booking["start_time"], "%H:%M").time()
#                 end_time = datetime.strptime(pending_booking["end_time"], "%H:%M").time()

#                 # ✅ Prefer actual transaction ID for refunds
#                 transaction_id = response_data.get("transaction_id") or pidx  # fallback to pidx

#                 booking = Booking.objects.create(
#                     artist=artist,
#                     client=client,
#                     service=service,
#                     date=date,
#                     start_time=start_time,
#                     end_time=end_time,
#                     latitude=pending_booking.get("latitude"),
#                     longitude=pending_booking.get("longitude"),
#                     payment_method="Khalti",
#                     status="Confirmed",
#                     transaction_id=transaction_id,  # ✅ Save transaction_id (real or fallback)
#                 )

#                 send_confirmation_email(booking)
#                 del request.session["pending_booking"]

#                 return JsonResponse({"success": "Payment verified and booking confirmed!"})

#             except Exception as e:
#                 return JsonResponse({"error": f"Error saving booking: {str(e)}"}, status=500)

#         else:
#             return JsonResponse({"error": "Payment verification failed!", "details": response_data}, status=400)

#     return JsonResponse({"error": "Invalid request!"}, status=400) 0331
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Booking, Service, User
import requests
import json

# ✅ Helper to check if the slot is still available
def is_slot_available(artist, date, start_time, end_time):
    return not Booking.objects.filter(
        artist=artist,
        date=date,
        start_time=start_time,
        end_time=end_time
    ).exclude(
        status__in=["Cancelled", "Completed"]
    ).exists()

# ✅ Verify Khalti Payment and confirm booking
@csrf_exempt
def verify_khalti_payment(request):
    if request.method == "POST":
        pidx = request.POST.get("pidx")

        if not pidx:
            return JsonResponse({"error": "Invalid Payment ID!"}, status=400)

        payload = {"pidx": pidx}
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY.strip()}",
            "Content-Type": "application/json",
        }

        print("🔍 Verifying Payment at Khalti")
        print("Payload:", payload)
        print("Headers:", headers)

        response = requests.post(f"{settings.KHALTI_API_URL}epayment/lookup/", json=payload, headers=headers)

        try:
            response_data = response.json()
            print("📨 Khalti Verification Response:", response_data)
        except Exception as e:
            print("❌ JSON Decode Error:", response.text)
            return JsonResponse({"error": "Invalid JSON from Khalti."}, status=400)

        if response_data.get("status") == "Completed":
            pending_booking = request.session.get("pending_booking")

            if not pending_booking or "client_id" not in pending_booking:
                return JsonResponse({"error": "No client ID found in booking data!"}, status=400)

            try:
                artist = get_object_or_404(User, id=pending_booking["artist_id"], is_artist=True)
                client = get_object_or_404(User, id=pending_booking["client_id"])
                service = get_object_or_404(Service, id=pending_booking["service_id"])

                date = datetime.strptime(pending_booking["date"], "%Y-%m-%d").date()
                start_time = datetime.strptime(pending_booking["start_time"], "%H:%M").time()
                end_time = datetime.strptime(pending_booking["end_time"], "%H:%M").time()

                # ✅ Check for time slot availability (exclude cancelled/completed)
                if not is_slot_available(artist, date, start_time, end_time):
                    return JsonResponse({"error": "This time slot is already booked. Please choose a different time."}, status=400)

                transaction_id = response_data.get("transaction_id") or pidx  # Fallback to pidx if not available

                # ✅ Save booking
                booking = Booking.objects.create(
                    artist=artist,
                    client=client,
                    service=service,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    latitude=pending_booking.get("latitude"),
                    longitude=pending_booking.get("longitude"),
                    payment_method="Khalti",
                    status="Confirmed",
                    transaction_id=transaction_id,
                )

                # ✅ Optional: Send confirmation email
                send_confirmation_email(booking)

                # ✅ Clear session
                del request.session["pending_booking"]

                return JsonResponse({"success": "Payment verified and booking confirmed!"})

            except Exception as e:
                return JsonResponse({"error": f"Error saving booking: {str(e)}"}, status=500)

        else:
            return JsonResponse({"error": "Payment verification failed!", "details": response_data}, status=400)

    return JsonResponse({"error": "Invalid request!"}, status=400)



def is_slot_available(artist, date, start_time, end_time):
    return not Booking.objects.filter(
        artist=artist,
        date=date,
        start_time=start_time,
        end_time=end_time
    ).exclude(
        status__in=["Cancelled", "Completed"]
    ).exists()


from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import os

def send_confirmation_email(booking):
    """ Sends separate emails to the client and artist with booking details. """
    
    # ✅ Email to the Client
    client_subject = "🎉 Booking Confirmed with {}".format(booking.artist.get_full_name())
    client_html_message = render_to_string("emails/booking_confirmation.html", {
        "user": booking.client,
        "artist": booking.artist,
        "service": booking.service,
        "date": booking.date.strftime("%A, %B %d, %Y"),
        "start_time": booking.start_time.strftime("%I:%M %p"),
        "end_time": booking.end_time.strftime("%I:%M %p"),
        "payment_method": booking.payment_method,
        "support_url": f"{settings.SITE_URL}/support/",
    })
    client_plain_message = strip_tags(client_html_message)
    client_recipient_list = [booking.client.email]

    try:
        client_email = EmailMessage(client_subject, client_html_message, settings.DEFAULT_FROM_EMAIL, client_recipient_list)
        client_email.content_subtype = "html"

        # ✅ Attach Logo (Optional)
        logo_path = os.path.join(settings.BASE_DIR, "static/images/logo.png")
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo:
                client_email.attach("logo.png", logo.read(), "image/png")

        client_email.send()
        print(f"✅ Email sent to client: {booking.client.email}")

    except Exception as e:
        print(f"❌ Error sending email to client: {str(e)}")


    # ✅ Email to the Artist
    artist_subject = "📩 New Booking from {}".format(booking.client.get_full_name())
    artist_html_message = render_to_string("emails/booking_notification_artist.html", {
        "artist": booking.artist,
        "client": booking.client,
        "service": booking.service,
        "date": booking.date.strftime("%A, %B %d, %Y"),
        "start_time": booking.start_time.strftime("%I:%M %p"),
        "end_time": booking.end_time.strftime("%I:%M %p"),
        "payment_method": booking.payment_method,
        "support_url": f"{settings.SITE_URL}/support/",
    })
    artist_plain_message = strip_tags(artist_html_message)
    artist_recipient_list = [booking.artist.email]

    try:
        artist_email = EmailMessage(artist_subject, artist_html_message, settings.DEFAULT_FROM_EMAIL, artist_recipient_list)
        artist_email.content_subtype = "html"

        # ✅ Attach Logo (Optional)
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as logo:
                artist_email.attach("logo.png", logo.read(), "image/png")

        artist_email.send()
        print(f"✅ Email sent to artist: {booking.artist.email}")

    except Exception as e:
        print(f"❌ Error sending email to artist: {str(e)}")

from django.shortcuts import render

def payment_success(request):
    return render(request, "payment_success.html", {"message": "Payment Successful!"})




# import json
# import logging
# from datetime import datetime
# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .models import Booking, Service, User

# logger = logging.getLogger(__name__)

# @login_required
# def book_artist(request, artist_id):
#     """ View for booking an artist's service """
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     services = Service.objects.filter(artist=artist)

#     # ✅ Prepare service data with correct workdays and available schedules
#     service_data = []
#     for service in services:
#         work_days = service.work_days.all()
#         work_days_list = [work_day.day for work_day in work_days]

#         # ✅ Generate all possible schedules
#         schedules = {}
#         for work_day in work_days:
#             all_slots = service.generate_slots_for_day(work_day)
#             schedules[work_day.day] = all_slots  # Initially store all slots

#         service_data.append({
#             "id": service.id,
#             "service_name": service.service_name,
#             "price": float(service.price),
#             "description": service.description,
#             "duration": service.get_total_duration_hms(),
#             "work_days": ",".join(work_days_list),
#             "schedules": schedules,
#         })

#     if request.method == "POST":
#         try:
#             # ✅ Ensure user is logged in before proceeding
#             if not request.user.is_authenticated:
#                 return JsonResponse({"error": "User must be logged in to book!"}, status=403)

#             data = json.loads(request.body)
#             service_id = data.get("service_id")
#             date_str = data.get("date")
#             selected_schedule = data.get("schedule")

#             if not service_id or not date_str or not selected_schedule:
#                 return JsonResponse({"error": "Missing required fields!"}, status=400)

#             service = get_object_or_404(Service, id=service_id, artist=artist)
#             booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

#             # ✅ Fetch only booked slots for the selected date
#             booked_slots = Booking.objects.filter(
#                 artist=artist,
#                 service=service,
#                 date=booking_date
#             ).values_list("start_time", "end_time")

#             # ✅ Format booked slots into "HH:MM - HH:MM"
#             booked_slots_formatted = [
#                 f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
#                 for start_time, end_time in booked_slots
#             ]

#             # ✅ Check if the selected schedule is already booked
#             if selected_schedule in booked_slots_formatted:
#                 return JsonResponse({"error": "This time slot is already booked. Please choose another slot."}, status=400)

#             # ✅ Update available schedules dynamically for the selected date
#             weekday_name = booking_date.strftime('%A')
#             for service_item in service_data:
#                 if service_item["id"] == service.id:
#                     if weekday_name in service_item["schedules"]:
#                         available_slots = [
#                             slot for slot in service_item["schedules"][weekday_name] if slot not in booked_slots_formatted
#                         ]
#                         service_item["schedules"][weekday_name] = available_slots  # ✅ Remove booked slots dynamically

#             # ✅ Store session data for payment processing
#             request.session["pending_booking"] = {
#                 "artist_id": artist.id,
#                 "client_id": request.user.id,
#                 "service_id": service.id,
#                 "date": date_str,
#                 "start_time": selected_schedule.split(" - ")[0].strip(),
#                 "end_time": selected_schedule.split(" - ")[1].strip(),
#                 "latitude": data.get("latitude"),
#                 "longitude": data.get("longitude"),
#                 "payment_method": data.get("payment_method"),
#             }

#             logger.info("📌 SESSION DATA AFTER FIX: %s", request.session["pending_booking"])

#             return JsonResponse({"success": "Booking request stored! Proceed to payment."}, status=200)

#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

#     return render(request, "accounts/book_artist.html", {
#         "artist": artist,
#         "services": json.dumps(service_data)
#     }) 030303
# import json
# import logging
# from datetime import datetime
# from django.shortcuts import render, get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .models import Booking, Service, User

# logger = logging.getLogger(__name__)

# @login_required
# def book_artist(request, artist_id):
#     """ View for booking an artist's service """
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     services = Service.objects.filter(artist=artist)

#     # Prepare service data with correct workdays and available schedules
#     service_data = []
#     for service in services:
#         work_days = service.work_days.all()
#         work_days_list = [work_day.day for work_day in work_days]

#         # Generate all possible schedules
#         schedules = {}
#         for work_day in work_days:
#             all_slots = service.generate_slots_for_day(work_day)
#             schedules[work_day.day] = all_slots

#         service_data.append({
#             "id": service.id,
#             "service_name": service.service_name,
#             "price": float(service.price),
#             "description": service.description,
#             "duration": service.get_total_duration_hms(),
#             "work_days": ",".join(work_days_list),
#             "schedules": schedules,
#         })

#     if request.method == "POST":
#         try:
#             if not request.user.is_authenticated:
#                 return JsonResponse({"error": "User must be logged in to book!"}, status=403)

#             data = json.loads(request.body)
#             service_id = data.get("service_id")
#             date_str = data.get("date")
#             selected_schedule = data.get("schedule")

#             if not service_id or not date_str or not selected_schedule:
#                 return JsonResponse({"error": "Missing required fields!"}, status=400)

#             service = get_object_or_404(Service, id=service_id, artist=artist)
#             booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

#             booked_slots = Booking.objects.filter(
#                 artist=artist,
#                 service=service,
#                 date=booking_date
#             ).values_list("start_time", "end_time")

#             booked_slots_formatted = [
#                 f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
#                 for start_time, end_time in booked_slots
#             ]

#             if selected_schedule in booked_slots_formatted:
#                 return JsonResponse({"error": "This time slot is already booked. Please choose another slot."}, status=400)

#             weekday_name = booking_date.strftime('%A')
#             for service_item in service_data:
#                 if service_item["id"] == service.id:
#                     if weekday_name in service_item["schedules"]:
#                         available_slots = [
#                             slot for slot in service_item["schedules"][weekday_name] if slot not in booked_slots_formatted
#                         ]
#                         service_item["schedules"][weekday_name] = available_slots

#             # Store session data for payment processing
#             request.session["pending_booking"] = {
#                 "artist_id": artist.id,
#                 "client_id": request.user.id,
#                 "service_id": service.id,
#                 "date": date_str,
#                 "start_time": selected_schedule.split(" - ")[0].strip(),
#                 "end_time": selected_schedule.split(" - ")[1].strip(),
#                 "latitude": data.get("latitude"),
#                 "longitude": data.get("longitude"),
#                 "payment_method": data.get("payment_method"),
#             }

#             logger.info("\ud83d\udccc SESSION DATA AFTER FIX: %s", request.session["pending_booking"])

#             return JsonResponse({"success": "Booking request stored! Proceed to payment."}, status=200)

#         except Exception as e:
#             logger.error(f"Unexpected error: {str(e)}")
#             return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

#     return render(request, "accounts/book_artist.html", {
#         "artist": artist,
#         "services": json.dumps(service_data)
#     }) 3103

import json
import logging
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Booking, Service, User

logger = logging.getLogger(__name__)

@login_required
def book_artist(request, artist_id):
    """ View for booking an artist's service """
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    services = Service.objects.filter(artist=artist)

    # Prepare service data with correct workdays and available schedules
    service_data = []
    for service in services:
        work_days = service.work_days.all()
        work_days_list = [work_day.day for work_day in work_days]

        # Generate all possible schedules
        schedules = {}
        for work_day in work_days:
            all_slots = service.generate_slots_for_day(work_day)
            schedules[work_day.day] = all_slots

        service_data.append({
            "id": service.id,
            "service_name": service.service_name,
            "price": float(service.price),
            "description": service.description,
            "duration": service.get_total_duration_hms(),
            "work_days": ",".join(work_days_list),
            "schedules": schedules,
        })

    if request.method == "POST":
        try:
            if not request.user.is_authenticated:
                return JsonResponse({"error": "User must be logged in to book!"}, status=403)

            data = json.loads(request.body)
            service_id = data.get("service_id")
            date_str = data.get("date")
            selected_schedule = data.get("schedule")

            if not service_id or not date_str or not selected_schedule:
                return JsonResponse({"error": "Missing required fields!"}, status=400)

            service = get_object_or_404(Service, id=service_id, artist=artist)
            booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()

            # ✅ Only check bookings that are NOT cancelled or completed
            booked_slots = Booking.objects.filter(
                artist=artist,
                service=service,
                date=booking_date
            ).exclude(
                status__in=["Cancelled", "Completed"]
            ).values_list("start_time", "end_time")

            booked_slots_formatted = [
                f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
                for start_time, end_time in booked_slots
            ]

            if selected_schedule in booked_slots_formatted:
                return JsonResponse({"error": "This time slot is already booked. Please choose another slot."}, status=400)

            weekday_name = booking_date.strftime('%A')
            for service_item in service_data:
                if service_item["id"] == service.id:
                    if weekday_name in service_item["schedules"]:
                        available_slots = [
                            slot for slot in service_item["schedules"][weekday_name] if slot not in booked_slots_formatted
                        ]
                        service_item["schedules"][weekday_name] = available_slots

            # Store session data for payment processing
            request.session["pending_booking"] = {
                "artist_id": artist.id,
                "client_id": request.user.id,
                "service_id": service.id,
                "date": date_str,
                "start_time": selected_schedule.split(" - ")[0].strip(),
                "end_time": selected_schedule.split(" - ")[1].strip(),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "payment_method": data.get("payment_method"),
            }

            logger.info("📌 SESSION DATA AFTER FIX: %s", request.session["pending_booking"])

            return JsonResponse({"success": "Booking request stored! Proceed to payment."}, status=200)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": f"Unexpected error: {str(e)}"}, status=500)

    return render(request, "accounts/book_artist.html", {
        "artist": artist,
        "services": json.dumps(service_data)
    })


# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Booking

# def get_booked_schedules(request):
#     """Fetch already booked schedules for a given artist, service, and date"""
#     artist_id = request.GET.get("artist_id")
#     service_id = request.GET.get("service_id")
#     date = request.GET.get("date")

#     # ✅ Log incoming request for debugging
#     print(f"📌 Received Request: Artist: {artist_id}, Service: {service_id}, Date: {date}")

#     if not artist_id or not service_id or not date:
#         print("❌ Error: Missing parameters!")
#         return JsonResponse({"error": "Missing parameters"}, status=400)

#     try:
#         # ✅ Ensure filtering only confirmed bookings
#         booked_schedules = Booking.objects.filter(
#             artist_id=artist_id,
#             service_id=service_id,
#             date=date,
#             status="Confirmed"
#         ).values_list("start_time", "end_time")

#         # ✅ Format booked schedules as ["HH:MM - HH:MM"]
#         formatted_booked_schedules = [
#             f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
#             for start_time, end_time in booked_schedules
#         ]

#         print(f"✅ Found booked schedules: {formatted_booked_schedules}")

#         return JsonResponse({"booked_schedules": formatted_booked_schedules})
    
#     except Exception as e:
#         print(f"❌ Error fetching schedules: {str(e)}")
#         return JsonResponse({"error": f"Failed to load schedules: {str(e)}"}, status=500)
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Booking

# def get_booked_schedules(request):
#     """Fetch all booked schedules for a given date (ignores artist and service)"""
    
#     date = request.GET.get("date")

#     # ✅ Log incoming request for debugging
#     print(f"📌 Received Request: Date: {date}")

#     if not date:
#         print("❌ Error: Missing date parameter!")
#         return JsonResponse({"error": "Missing date parameter"}, status=400)

#     try:
#         # ✅ Fetch all booked schedules for the selected date (ignore artist & service)
#         booked_schedules = Booking.objects.filter(
#             date=date,
#             status="Confirmed"
#         ).values_list("start_time", "end_time", flat=False)

#         # ✅ Format booked schedules as ["HH:MM - HH:MM"]
#         formatted_booked_schedules = list(set(
#             f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
#             for start_time, end_time in booked_schedules
#         ))

#         print(f"✅ Booked schedules for {date}: {formatted_booked_schedules}")

#         return JsonResponse({"booked_schedules": formatted_booked_schedules})
    
#     except Exception as e:
#         print(f"❌ Error fetching schedules: {str(e)}")
#         return JsonResponse({"error": f"Failed to load schedules: {str(e)}"}, status=500)
# from django.http import JsonResponse
# from django.db.models import Q
# from datetime import datetime, timedelta
# from .models import Booking

# def get_booked_schedules(request):
#     """Fetch booked schedules for a given date, considering all services"""
#     artist_id = request.GET.get("artist_id")
#     date = request.GET.get("date")

#     # ✅ Log incoming request for debugging
#     print(f"📌 Received Request: Artist: {artist_id}, Date: {date}")

#     if not artist_id or not date:
#         print("❌ Error: Missing parameters!")
#         return JsonResponse({"error": "Missing parameters"}, status=400)

#     try:
#         # ✅ Fetch all confirmed bookings for the artist and date (all services)
#         bookings = Booking.objects.filter(
#             artist_id=artist_id,
#             date=date,
#             status="Confirmed"
#         ).values_list("start_time", "end_time")

#         booked_schedules = []

#         for start_time, end_time in bookings:
#             # ✅ Convert start_time to datetime for arithmetic operations
#             start_datetime = datetime.combine(datetime.today(), start_time)
#             end_datetime = datetime.combine(datetime.today(), end_time)

#             # ✅ Add the exact booked time range
#             booked_schedules.append(f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

#             # ✅ Add 15-minute intervals to detect overlapping slots
#             current_time = start_datetime
#             while current_time < end_datetime:
#                 booked_schedules.append(current_time.time().strftime('%H:%M'))
#                 current_time += timedelta(minutes=15)  # Move in 15-minute steps

#         print(f"✅ Final booked schedules (all services): {booked_schedules}")

#         return JsonResponse({"booked_schedules": booked_schedules})

#     except Exception as e:
#         print(f"❌ Error fetching schedules: {str(e)}")
#         return JsonResponse({"error": f"Failed to load schedules: {str(e)}"}, status=500) 3103

from django.http import JsonResponse
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Booking

def get_booked_schedules(request):
    """Fetch booked schedules for a given date, considering all services"""
    artist_id = request.GET.get("artist_id")
    date = request.GET.get("date")

    print(f"📌 Received Request: Artist: {artist_id}, Date: {date}")

    if not artist_id or not date:
        print("❌ Error: Missing parameters!")
        return JsonResponse({"error": "Missing parameters"}, status=400)

    try:
        # ✅ Only include bookings that are NOT Cancelled or Completed
        bookings = Booking.objects.filter(
            artist_id=artist_id,
            date=date
        ).exclude(
            status__in=["Cancelled", "Completed"]
        ).values_list("start_time", "end_time")

        booked_schedules = []

        for start_time, end_time in bookings:
            start_datetime = datetime.combine(datetime.today(), start_time)
            end_datetime = datetime.combine(datetime.today(), end_time)

            # Add the full time range
            booked_schedules.append(f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")

            # Add 15-minute intervals
            current_time = start_datetime
            while current_time < end_datetime:
                booked_schedules.append(current_time.time().strftime('%H:%M'))
                current_time += timedelta(minutes=15)

        print(f"✅ Final booked schedules (all services): {booked_schedules}")

        return JsonResponse({"booked_schedules": booked_schedules})

    except Exception as e:
        print(f"❌ Error fetching schedules: {str(e)}")
        return JsonResponse({"error": f"Failed to load schedules: {str(e)}"}, status=500)


import numpy as np
from sklearn.neighbors import NearestNeighbors
from .models import Service

def find_similar_services(budget, n=5):
    """
    Uses KNN to find the closest services within the user's budget.
    """
    services = list(Service.objects.all())  # Convert QuerySet to list
    prices = np.array([service.price for service in services]).reshape(-1, 1)

    if len(prices) == 0:
        return []

    # Train KNN model
    model = NearestNeighbors(n_neighbors=min(n, len(prices)), algorithm='auto')
    model.fit(prices)

    # Find services closest to the entered budget
    distances, indices = model.kneighbors([[budget]])

    # ✅ Convert int64 indices to Python integers before using them
    similar_services = [services[int(i)] for i in indices.flatten()]
    
    return similar_services
# from django.shortcuts import render
# from django.db.models import Min, Max
# from .models import User, Service

# def artist_list(request):
#     # ✅ Fetch all artists with services efficiently
#     artists = User.objects.filter(is_artist=True).prefetch_related('services')

#     # ✅ Get distinct cities for filtering
#     cities = artists.values_list('city', flat=True).distinct()

#     # ✅ Get min and max price dynamically
#     price_stats = Service.objects.aggregate(min_price=Min("price"), max_price=Max("price"))

#     min_price = price_stats["min_price"] or 0
#     max_price = price_stats["max_price"] or 0

#     # ✅ Apply Filters from GET request
#     selected_city = request.GET.get("city", "all")
#     entered_price = request.GET.get("entered_price", "").strip()  # Get typed price

#     # Filter by City
#     if selected_city and selected_city != "all":
#         artists = artists.filter(city__iexact=selected_city)

#     # Apply KNN filtering for Price (if price is entered)
#     filtered_services = []
#     if entered_price:
#         try:
#             budget = float(entered_price)
#             filtered_services = find_similar_services(budget)
#         except ValueError:
#             pass  # Ignore invalid inputs

#     # Show only artists that offer the filtered services
#     if filtered_services:
#         artist_ids = [service.artist.id for service in filtered_services]
#         artists = artists.filter(id__in=artist_ids)

#     return render(request, "accounts/artist_list.html", {
#         "artists": artists,
#         "cities": cities,
#         "min_price": min_price,
#         "max_price": max_price,
#         "entered_price": entered_price  # Send back user input
#     })
from django.shortcuts import render
from django.db.models import Min, Max, Q
from .models import User, Service

def artist_list(request):
    # ✅ Fetch all artists with services efficiently
    artists = User.objects.filter(is_artist=True).prefetch_related('services')

    # ✅ Get distinct cities for filtering
    cities = artists.values_list('city', flat=True).distinct()

    # ✅ Get min and max price dynamically
    price_stats = Service.objects.aggregate(min_price=Min("price"), max_price=Max("price"))
    min_price = price_stats["min_price"] or 0
    max_price = price_stats["max_price"] or 0

    # ✅ Get filter values from GET request
    selected_city = request.GET.get("city", "all")
    entered_price = request.GET.get("entered_price", "").strip()
    keyword = request.GET.get("keyword", "").strip()

    # ✅ Filter by City
    if selected_city and selected_city != "all":
        artists = artists.filter(city__iexact=selected_city)

    # ✅ Build service filter query
    service_filter = Q()
    if entered_price:
        try:
            budget = float(entered_price)
            service_filter &= Q(price__lte=budget)
        except ValueError:
            pass  # Ignore invalid input

    if keyword:
        service_filter &= Q(service_name__icontains=keyword)

    # ✅ Filter services and artist list based on service filter
    if service_filter:
        filtered_services = Service.objects.filter(service_filter)
        artist_ids = filtered_services.values_list("artist__id", flat=True).distinct()
        artists = artists.filter(id__in=artist_ids)

    return render(request, "accounts/artist_list.html", {
        "artists": artists,
        "cities": cities,
        "min_price": min_price,
        "max_price": max_price,
        "entered_price": entered_price,
        "keyword": keyword,
    })


from django.shortcuts import render
from .models import Booking  # Replace with your actual model import
from django.contrib.auth.decorators import login_required

@login_required
def refund_view(request):
    # ✅ Correct
    cancelled_bookings = Booking.objects.filter(client=request.user, status="Cancelled").order_by('-date')
    return render(request, 'accounts/refund.html', {'cancelled_bookings': cancelled_bookings})

# def claim_khalti_refund(request, booking_id):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "Invalid request method."})

#     booking = get_object_or_404(Booking, id=booking_id, client=request.user)

#     if booking.status != "Cancelled" or booking.payment_method.lower() != "khalti":
#         return JsonResponse({"success": False, "error": "Refund not allowed for this booking."})

#     if booking.refund_requested:
#         return JsonResponse({"success": False, "error": "Refund already requested."})

#     # Simulate refund request, mark as requested
#     booking.refund_requested = True
#     booking.save()

#     return JsonResponse({
#         "success": True,
#         "message": "Refund request has been submitted. Our team will verify and process it shortly."
#     })
# from django.views.decorators.csrf import csrf_exempt
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from django.conf import settings
# from .models import Booking
# import requests

# @csrf_exempt
# def claim_khalti_refund(request, booking_id):
#     if request.method != "POST":
#         return JsonResponse({"success": False, "error": "Invalid request method."})

#     booking = get_object_or_404(Booking, id=booking_id, client=request.user)

#     if booking.status != "Cancelled" or booking.payment_method.lower() != "khalti":
#         return JsonResponse({"success": False, "error": "Refund not allowed for this booking."})

#     if booking.refund_requested:
#         return JsonResponse({"success": False, "error": "Refund already requested."})

#     if not booking.transaction_id:
#         return JsonResponse({"success": False, "error": "Missing transaction ID."})

#     try:
#         # ✅ Use Sandbox refund endpoint
#         # endpoint = f"https://dev.khalti.com/api/merchant-transaction/YeFanerndU4P25nQKGvKLT/refund/"
#         endpoint = f"https://dev.khalti.com/api/merchant-transaction/{booking.transaction_id}/refund/"


#         headers = {
#             "Authorization": f"Key {settings.KHALTI_SECRET_KEY.replace('live_', '').strip()}",
#             "Content-Type": "application/json",
#         }

#         print("\n🌍 ENVIRONMENT: SANDBOX")
#         print(f"🔑 Using Secret Key: {settings.KHALTI_SECRET_KEY.replace('live_', '').strip()}")
#         print(f"🔁 Refund Request Sent to Khalti Wallet: {endpoint}")
#         print("🔑 Headers:", headers)

#         response = requests.post(endpoint, headers=headers)

#         if response.status_code != 200:
#             print("❌ Non-200 status code:", response.status_code)
#             print("❌ Raw response:", response.text)
#             try:
#                 error_detail = response.json().get("detail", "Unknown error")
#             except ValueError:
#                 error_detail = response.text
#             return JsonResponse({
#                 "success": False,
#                 "error": f"Refund failed with status {response.status_code}: {error_detail}"
#             })

#         try:
#             response_data = response.json()
#         except ValueError:
#             print("❌ HTML/Non-JSON Response:", response.text)
#             return JsonResponse({"success": False, "error": "Invalid response format received from Khalti."})

#         print("📨 Refund Response:", response_data)

#         if response_data.get("status") == "Completed" or response_data.get("refunded") is True:
#             booking.refund_requested = True
#             booking.save()
#             return JsonResponse({"success": True, "message": "Refund processed successfully."})
#         else:
#             error_message = response_data.get("detail") or response_data.get("message") or "Refund not completed."
#             return JsonResponse({
#                 "success": False,
#                 "error": f"Refund failed: {error_message}",
#                 "response": response_data
#             })

#     except Exception as e:
#         print("❌ Exception:", str(e))
#         return JsonResponse({"success": False, "error": f"Error processing refund: {str(e)}"})
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail  # ✅ Add this
from django.conf import settings
from .models import Booking
import requests
def send_refund_email(booking):
    subject = "💸 Refund Processed Successfully"
    message = (
        f"Hi {booking.client.first_name},\n\n"
        f"Your refund for the booking with {booking.artist.get_full_name()} "
        f"on {booking.date} from {booking.start_time.strftime('%I:%M %p')} to {booking.end_time.strftime('%I:%M %p')} "
        f"has been successfully processed via Khalti.\n\n"
        f"If you have any questions, feel free to contact us.\n\n"
        f"Thank you!"
    )
    recipient_list = [booking.client.email]
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

@csrf_exempt
def claim_khalti_refund(request, booking_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method."})

    booking = get_object_or_404(Booking, id=booking_id, client=request.user)

    if booking.status != "Cancelled" or booking.payment_method.lower() != "khalti":
        return JsonResponse({"success": False, "error": "Refund not allowed for this booking."})

    if booking.refund_requested:
        return JsonResponse({"success": False, "error": "Refund already requested."})

    if not booking.transaction_id:
        return JsonResponse({"success": False, "error": "Missing transaction ID."})

    try:
        endpoint = f"https://dev.khalti.com/api/merchant-transaction/{booking.transaction_id}/refund/"
        headers = {
            "Authorization": f"Key {settings.KHALTI_SECRET_KEY.replace('live_', '').strip()}",
            "Content-Type": "application/json",
        }

        print("\n🌍 ENVIRONMENT: SANDBOX")
        print(f"🔑 Using Secret Key: {settings.KHALTI_SECRET_KEY.replace('live_', '').strip()}")
        print(f"🔁 Refund Request Sent to Khalti Wallet: {endpoint}")
        print("🔑 Headers:", headers)

        response = requests.post(endpoint, headers=headers)

        if response.status_code != 200:
            print("❌ Non-200 status code:", response.status_code)
            print("❌ Raw response:", response.text)
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except ValueError:
                error_detail = response.text
            return JsonResponse({
                "success": False,
                "error": f"Refund failed with status {response.status_code}: {error_detail}"
            })

        try:
            response_data = response.json()
        except ValueError:
            print("❌ HTML/Non-JSON Response:", response.text)
            return JsonResponse({"success": False, "error": "Invalid response format received from Khalti."})

        print("📨 Refund Response:", response_data)

        detail_msg = response_data.get("detail", "").lower()
        if (
            response_data.get("status") == "Completed"
            or response_data.get("refunded") is True
            or "successful" in detail_msg
        ):
            booking.refund_requested = True
            booking.save()
            send_refund_email(booking)
            return JsonResponse({"success": True, "message": "✅ Refund processed successfully!"})
        else:
            error_message = response_data.get("detail") or response_data.get("message") or "Refund not completed."
            return JsonResponse({
                "success": False,
                "error": f"Refund failed: {error_message}",
                "response": response_data
            })

    except Exception as e:
        print("❌ Exception:", str(e))
        return JsonResponse({"success": False, "error": f"Error processing refund: {str(e)}"})
