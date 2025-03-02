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

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q  # ✅ Import Avg, Count, and Q
from .models import User, Booking, Review

@login_required(login_url='login')
def home_page(request):
    user = request.user
    query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

    # ✅ Step 1: Get All Artists (Keep Unavailable in Main List)
    artists = User.objects.filter(is_artist=True)  # Keep all artists (available & unavailable)
    
    if query:
        artists = artists.filter(city__icontains=query)

    # ✅ Step 2: Annotate Artists with Average Rating
    artists = artists.annotate(
        avg_rating=Avg('artist_reviews__rating'),  # ✅ Correct annotation
        appointment_count=Count('bookings', filter=Q(bookings__status="Confirmed"))
    )

    # ✅ Step 3: Sorting Logic
    if sort_by == "rating":
        artists = artists.order_by('-avg_rating')  # ✅ Sort by average rating
    elif sort_by == "appointments":
        artists = artists.order_by('-appointment_count')  # ✅ Sort by confirmed appointments

    # ✅ Step 4: Paginate Artists (10 per page)
    paginator = Paginator(artists, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ✅ Step 5: Fetch Booked Artists by User
    user_bookings = Booking.objects.filter(client=user, status="Confirmed").order_by('-date')
    booked_artist_ids = user_bookings.values_list('artist_id', flat=True)

    # ✅ Step 6: AI-BASED RECOMMENDATION LOGIC (ONLY AVAILABLE ARTISTS)
    recommended_artists = []

    if booked_artist_ids:
        # ✅ Find users who booked the same artists
        similar_users = Booking.objects.filter(artist_id__in=booked_artist_ids).values_list("client_id", flat=True).distinct()

        if similar_users:
            recommended_artists = User.objects.filter(
                is_artist=True,
                is_available=True,
                bookings__client_id__in=similar_users
            ).exclude(id__in=booked_artist_ids).annotate(
                booking_count=Count("bookings")
            ).order_by("-booking_count")[:5]

    # ✅ Step 7: Check Latest Booking City (ONLY AVAILABLE ARTISTS)
    if not recommended_artists and user_bookings.exists():
        latest_booking = user_bookings.first()
        latest_artist_city = latest_booking.artist.city

        recommended_artists = User.objects.filter(
            is_artist=True,
            is_available=True,
            city=latest_artist_city
        ).exclude(id=user.id).annotate(avg_rating=Avg('artist_reviews__rating')).order_by('-avg_rating')[:5]

    # ✅ Step 8: Fallback to Artists from the Same City (ONLY AVAILABLE ARTISTS)
    if not recommended_artists and user.city:
        recommended_artists = User.objects.filter(
            is_artist=True,
            is_available=True,
            city=user.city
        ).exclude(id=user.id).annotate(avg_rating=Avg('artist_reviews__rating')).order_by('-avg_rating')[:5]

    # ✅ Step 9: Fallback to Top-Rated Artists (ONLY AVAILABLE ARTISTS)
    if not recommended_artists:
        recommended_artists = artists.filter(is_available=True).order_by('-avg_rating')[:5]

    # ✅ Fetch Latest Artist Reviews
    artist_reviews = Review.objects.select_related("artist", "user").order_by("-created_at")[:10]

    return render(request, "accounts/home.html", {
        "artists": page_obj,  # ✅ Keep all artists (available & unavailable)
        "recommended_artists": recommended_artists,  # ✅ Remove unavailable artists from recommendations
        "artist_reviews": artist_reviews,  # Latest Artist Reviews
        "query": query,
        "message": "No artists found in this city." if not artists.exists() else "",
        "booked_artists": list(booked_artist_ids),  # List of booked artist IDs
        "sort_by": sort_by,
    })



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




from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking, ServiceSchedule
import logging

# ✅ Setup logging for debugging
logger = logging.getLogger(__name__)

@login_required
def cancel_booking(request, booking_id):
    """ ✅ Cancel a booking and make the time slot available again """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    try:
        # ✅ Retrieve the booking for the logged-in user
        booking = get_object_or_404(Booking, id=booking_id, client=request.user)

        if booking.status not in ["Pending", "Confirmed"]:
            return JsonResponse({"success": False, "message": "Cannot cancel this booking."}, status=400)

        # ✅ Get the weekday from the booking date
        weekday = booking.date.strftime("%A")  # Example: "Monday"

        # ✅ Retrieve the corresponding service schedule
        schedule = ServiceSchedule.objects.filter(
            service=booking.service,
            weekday=weekday,
            start_time=booking.time  # ✅ Using `start_time`
        ).first()

        if schedule:
            logger.info(f"✅ Schedule found: {schedule.service.service_name} on {weekday} at {schedule.start_time}")

        # ✅ Update booking status
        booking.status = "Cancelled"
        booking.save()
        logger.info(f"✅ Booking {booking.id} successfully cancelled.")

        messages.success(request, "Your booking has been canceled.")

        return JsonResponse({
            "success": True,
            "message": "Booking canceled.",
            "booking_id": booking.id,
            "service_id": booking.service.id,
            "date": booking.date.strftime("%Y-%m-%d"),
            "weekday": weekday
        })

    except Booking.DoesNotExist:
        return JsonResponse({"success": False, "message": "Booking not found."}, status=404)
    
    except Exception as e:
        logger.error(f"❌ Error cancelling booking: {e}")
        return JsonResponse({"success": False, "message": "An error occurred while cancelling the booking."}, status=500)



from django.shortcuts import render, get_object_or_404, redirect
from django.forms import modelformset_factory
from .models import Service, ServiceAvailability
from .forms import ServiceForm, ServiceAvailabilityForm

def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    # ✅ Formset to manage availability slots dynamically
    ServiceAvailabilityFormSet = modelformset_factory(
        ServiceAvailability, 
        form=ServiceAvailabilityForm, 
        extra=1,  # Allows adding extra slots dynamically
        can_delete=True  # Allows removing slots
    )

    if request.method == "POST":
        service_form = ServiceForm(request.POST, instance=service)
        formset = ServiceAvailabilityFormSet(request.POST, queryset=ServiceAvailability.objects.filter(service=service))

        if service_form.is_valid() and formset.is_valid():
            service = service_form.save()  # ✅ Save edited service

            # ✅ Handle formset availability slots
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
                    availability = form.save(commit=False)
                    availability.service = service
                    availability.save()

            # ✅ Delete removed slots
            for form in formset.deleted_forms:
                if form.instance.pk:
                    form.instance.delete()

            return redirect("services")  # ✅ Redirect to services page

    else:
        service_form = ServiceForm(instance=service)
        formset = ServiceAvailabilityFormSet(queryset=ServiceAvailability.objects.filter(service=service))

    return render(request, "accounts/edit_service.html", {
        "service": service,
        "service_form": service_form,
        "availability_formset": formset,
    })


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

# ✅ Artist Dashboard
@login_required(login_url='artist_login')
def artist_dashboard(request):
    artist = request.user
    if not artist.is_artist:
        return redirect('artist_login')

    works = Work.objects.filter(artist=artist)
    return render(request, 'accounts/artist_dashboard.html', {'works': works})


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

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Service, Review

@login_required(login_url='artist_login')  # Ensure user is logged in before accessing services
def services(request):
    artist_services = Service.objects.filter(artist=request.user).prefetch_related('service_reviews')  # Efficiently load reviews
    return render(request, 'accounts/services.html', {'services': artist_services})









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
from .models import ServiceSchedule

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



from django.shortcuts import render
from .models import User, Service  # Ensure Service model exists

def artist_list(request):
    # ✅ Fetch all artists with services
    artists = User.objects.filter(is_artist=True).prefetch_related('services')

    # ✅ Get distinct cities for filtering
    cities = artists.values_list('city', flat=True).distinct()

    # ✅ Extract unique prices from services
    prices = list(Service.objects.filter(artist__in=artists).values_list('price', flat=True))

    price_ranges = []
    
    if prices:
        min_price = min(prices)
        max_price = max(prices)

        # ✅ Dynamically set step based on price spread
        price_spread = max_price - min_price
        if price_spread <= 1000:
            step = 500  # Smaller spread → Smaller steps
        elif price_spread <= 5000:
            step = 1000  # Medium spread → Medium steps
        else:
            step = 2000  # Large spread → Wider steps

        # ✅ Generate price ranges
        start = min_price
        while start < max_price:
            end = start + step
            if end >= max_price:
                price_ranges.append(f"{start}+")
                break
            else:
                price_ranges.append(f"{start}-{end}")
            start = end

    return render(request, "accounts/artist_list.html", {
        "artists": artists,
        "cities": cities,
        "price_ranges": price_ranges,  # ✅ Smarter ranges
    })



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





from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from datetime import date
from .models import Booking, Service, User, ServiceAvailability

# import logging
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.contrib import messages
# from django.core.mail import send_mail
# from datetime import date
# from .models import Booking, Service, User, ServiceAvailability

# # Initialize logger
# logger = logging.getLogger(__name__)

# @login_required
# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         date_selected = request.POST.get("date")
#         time_selected = request.POST.get("time")
#         service_id = request.POST.get("service")
#         payment_method = request.POST.get("payment_method")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")

#         logger.info(f"Received booking request from {user.email} for {artist.first_name}")

#         # ✅ Validate required fields
#         if not date_selected or not time_selected or not service_id or not payment_method:
#             return JsonResponse({"status": "error", "message": "All fields are required."})

#         # ✅ Ensure selected date is not in the past
#         if date.fromisoformat(date_selected) < date.today():
#             return JsonResponse({"status": "error", "message": "You cannot book past dates."})

#         selected_service = get_object_or_404(Service, id=service_id, artist=artist)

#         # ✅ Ensure the selected time slot exists in ServiceAvailability
#         if not ServiceAvailability.objects.filter(
#             service=selected_service, available_date=date_selected, available_time=time_selected
#         ).exists():
#             return JsonResponse({"status": "error", "message": "The selected time slot is not available."})

#         # ✅ Check if the artist is already booked at this date & time
#         if Booking.objects.filter(artist=artist, date=date_selected, time=time_selected).exists():
#             return JsonResponse({"status": "error", "message": "This time slot is already booked. Choose another."})

#         # ✅ Save booking with latitude & longitude
#         booking = Booking.objects.create(
#             artist=artist,
#             client=user,
#             date=date_selected,
#             time=time_selected,
#             service=selected_service,
#             payment_method=payment_method,
#             latitude=latitude,
#             longitude=longitude,
#             status="Pending"  # ✅ Default to pending until confirmed
#         )

#         logger.info(f"Booking created successfully: {booking.id}")

#         # ✅ Send confirmation email
#         try:
#             send_mail(
#                 "Booking Received - Artist Finder",
#                 f"Dear {user.first_name},\n\nYour booking for {selected_service.service_name} with {artist.first_name} {artist.last_name} on {date_selected} at {time_selected} has been received.\n\nYou will get a confirmation mail soon!\n\nThank you for using Artist Finder!",
#                 "no-reply@artistfinder.com",
#                 [user.email],
#                 fail_silently=False,
#             )
#             logger.info("Confirmation email sent successfully!")
#         except Exception as e:
#             logger.error(f"Failed to send email: {e}")

#         return JsonResponse({
#             "status": "success",
#             "message": "Your booking has been listed. You will receive a confirmation message soon.",
#         })

#     return render(request, 'accounts/book_artist.html', {
#         'artist': artist,
#         'user': user,
#         'services': services
#     })
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import User, Service, ServiceAvailability, Booking
from django.utils.timezone import now

# @login_required
# def book_artist(request, artist_id):
#     # Fetch artist and associated services
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         # Retrieve form data
#         date_selected = request.POST.get("date")
#         time_selected = request.POST.get("time")
#         service_id = request.POST.get("service")
#         payment_method = request.POST.get("payment_method")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")

#         # Split time range and convert to time objects
#         try:
#             start_time_str, end_time_str = time_selected.split(" - ")
#             start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
#             end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
#         except ValueError:
#             return JsonResponse({"status": "error", "message": "Invalid time format."})

#         # Ensure the selected time slot exists in ServiceAvailability
#         available_slots = ServiceAvailability.objects.filter(
#             service__artist=artist,
#             available_date=date_selected
#         )

#         is_available = False
#         for slot in available_slots:
#             # Check for time overlap
#             if slot.start_time <= start_time and slot.end_time >= end_time:
#                 is_available = True
#                 break

#         if not is_available:
#             return JsonResponse({"status": "error", "message": "The selected time slot is not available."})

#         # Prevent duplicate booking for same artist, date, and time
#         if Booking.objects.filter(artist=artist, date=date_selected, time=start_time).exists():
#             return JsonResponse({"status": "error", "message": "This time slot is already booked. Please select another."})

#         # Proceed with creating the booking
#         service = get_object_or_404(Service, id=service_id)
#         booking = Booking(
#             artist=artist,
#             client=user,
#             service=service,
#             date=date_selected,
#             time=start_time,
#             payment_method=payment_method,
#             latitude=latitude,
#             longitude=longitude
#         )
#         booking.save()

#         # Mark the selected slot as booked in ServiceAvailability
#         available_slot = ServiceAvailability.objects.get(
#             service=service,
#             available_date=date_selected,
#             start_time=start_time,
#             end_time=end_time
#         )
#         available_slot.mark_as_booked()

#         return JsonResponse({"status": "success", "message": "Booking successfully created!"})

#     # If the method is not POST, render the booking page
#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})
# from django.shortcuts import get_object_or_404
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from datetime import datetime
# from .models import User, Service, ServiceAvailability, Booking

# @login_required
# def book_artist(request, artist_id):
#     # Fetch artist and associated services
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         # Retrieve form data
#         date_selected = request.POST.get("date")
#         time_selected = request.POST.get("time")
#         service_id = request.POST.get("service")
#         payment_method = request.POST.get("payment_method")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")

#         try:
#             start_time = datetime.strptime(time_selected, "%H:%M:%S").time()  # Ensure the time format is correctly parsed
#         except ValueError:
#             return JsonResponse({"status": "error", "message": "Invalid time format."})

#         # Ensure the selected time slot exists in ServiceAvailability
#         available_slots = ServiceAvailability.objects.filter(
#             service__artist=artist,
#             available_date=date_selected
#         )

#         is_available = False
#         for slot in available_slots:
#             # Check if the selected time slot is available (no overlap)
#             if slot.start_time <= start_time < slot.end_time:
#                 is_available = True
#                 break

#         if not is_available:
#             return JsonResponse({"status": "error", "message": "The selected time slot is not available."})

#         # Prevent duplicate booking for the same artist, date, and time
#         if Booking.objects.filter(artist=artist, date=date_selected, time=start_time).exists():
#             return JsonResponse({"status": "error", "message": "This time slot is already booked. Please select another."})

#         # Proceed with creating the booking
#         service = get_object_or_404(Service, id=service_id)
#         booking = Booking(
#             artist=artist,
#             client=user,
#             service=service,
#             date=date_selected,
#             time=start_time,
#             payment_method=payment_method,
#             latitude=latitude,
#             longitude=longitude
#         )
#         booking.save()

#         # Mark the selected slot as booked in ServiceAvailability
#         available_slot = ServiceAvailability.objects.get(
#             service=service,
#             available_date=date_selected,
#             start_time=start_time
#         )
#         available_slot.mark_as_booked()

#         return JsonResponse({"status": "success", "message": "Booking successfully created!"})

#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import User, Service, ServiceAvailability, Booking

# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Booking, Service, ServiceSchedule
# from datetime import datetime

# @login_required
# def book_artist(request, artist_id):
#     # Fetch artist and associated services
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         # Retrieve form data
#         date_selected = request.POST.get("date")
#         time_selected = request.POST.get("time")  # Time range in format 'HH:MM:SS - HH:MM:SS'
#         service_id = request.POST.get("service")
#         payment_method = request.POST.get("payment_method")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")

#         try:
#             # Split time range into start and end times
#             start_time_str, end_time_str = time_selected.split(" - ")
            
#             # Convert to time objects
#             start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
#             end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()

#         except ValueError:
#             return JsonResponse({"status": "error", "message": f"Invalid time format: '{time_selected}'. Please use the format HH:MM:SS - HH:MM:SS."})

#         # Ensure the selected time slot exists in ServiceSchedule
#         available_slots = ServiceSchedule.objects.filter(
#             service__artist=artist,
#             available_date=date_selected
#         )

#         is_available = False
#         for slot in available_slots:
#             # Check if the selected time slot overlaps with an available slot
#             if (slot.start_time <= start_time < slot.end_time) or (start_time < slot.start_time < end_time):
#                 is_available = True
#                 break

#         if not is_available:
#             return JsonResponse({"status": "error", "message": "The selected time slot is not available."})

#         # Prevent duplicate booking for the same artist, date, and time
#         if Booking.objects.filter(artist=artist, date=date_selected, time__range=(start_time, end_time)).exists():
#             return JsonResponse({"status": "error", "message": "This time slot is already booked. Please select another."})

#         # Proceed with creating the booking
#         service = get_object_or_404(Service, id=service_id)
#         booking = Booking(
#             artist=artist,
#             client=user,
#             service=service,
#             date=date_selected,
#             time=start_time,  # Use the start time as booking time
#             payment_method=payment_method,
#             latitude=latitude,
#             longitude=longitude
#         )
#         booking.save()

#         # Mark the selected slot as booked in ServiceSchedule
#         available_slot = ServiceSchedule.objects.get(
#             service=service,
#             available_date=date_selected,
#             start_time=start_time
#         )
#         available_slot.is_booked = True
#         available_slot.save()

#         return JsonResponse({"status": "success", "message": "Booking successfully created!"})

#     # If the method is not POST, render the booking page
#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})

# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Booking, Service
# from datetime import datetime

# @login_required
# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         date_selected = request.POST.get("date")
#         time_selected = request.POST.get("time")  # Time range in format 'HH:MM:SS - HH:MM:SS'
#         service_id = request.POST.get("service")
#         payment_method = request.POST.get("payment_method")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")

#         try:
#             start_time_str, end_time_str = time_selected.split(" - ")
#             start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
#             end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
#         except ValueError:
#             return JsonResponse({"status": "error", "message": f"Invalid time format: '{time_selected}'. Please use the format HH:MM:SS - HH:MM:SS."})

#         service = get_object_or_404(Service, id=service_id)
#         booking = Booking(
#             artist=artist,
#             client=user,
#             service=service,
#             date=date_selected,
#             time=start_time,
#             payment_method=payment_method,
#             latitude=latitude,
#             longitude=longitude
#         )
#         booking.save()

#         return JsonResponse({"status": "success", "message": "Booking successfully created!"})

#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})
# from django.core.mail import send_mail
# from django.conf import settings
# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Booking, Service
# from datetime import datetime

# @login_required
# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         # Retrieve form data
#         date_selected = request.POST.get("date")
#         time_selected = request.POST.get("time")
#         service_id = request.POST.get("service")
#         payment_method = request.POST.get("payment_method")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")

#         try:
#             start_time_str, end_time_str = time_selected.split(" - ")
#             start_time = datetime.strptime(start_time_str, "%H:%M:%S").time()
#             end_time = datetime.strptime(end_time_str, "%H:%M:%S").time()
#         except ValueError:
#             return JsonResponse({"status": "error", "message": f"Invalid time format: '{time_selected}'. Please use the format HH:MM:SS - HH:MM:SS."})

#         # Check if the selected time slot is available (and prevent duplicate bookings)
#         service = get_object_or_404(Service, id=service_id)
#         booking = Booking(
#             artist=artist,
#             client=user,
#             service=service,
#             date=date_selected,
#             time=start_time,
#             payment_method=payment_method,
#             latitude=latitude,
#             longitude=longitude
#         )
#         booking.save()

#         # Send confirmation email to client (user)
#         send_mail(
#             subject=f"Booking Confirmation - {artist.first_name} {artist.last_name}",
#             message=f"Dear {user.first_name},\n\nYour booking has been confirmed with {artist.first_name} {artist.last_name} for the service: {service.service_name}.\n\nBooking Details:\nDate: {date_selected}\nTime: {start_time}\nService: {service.service_name}\n\nPayment Method: {payment_method}\nLocation: Latitude: {latitude}, Longitude: {longitude}\n\nThank you for using our service!",
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[user.email],
#         )

#         # Send confirmation email to artist
#         send_mail(
#             subject=f"New Booking Received - {user.first_name} {user.last_name}",
#             message=f"Dear {artist.first_name},\n\nYou have received a new booking from {user.first_name} {user.last_name} for the service: {service.service_name}.\n\nBooking Details:\nDate: {date_selected}\nTime: {start_time}\nService: {service.service_name}\nClient: {user.first_name} {user.last_name}\n\nPayment Method: {payment_method}\nLocation: Latitude: {latitude}, Longitude: {longitude}\n\nPlease prepare accordingly.",
#             from_email=settings.EMAIL_HOST_USER,
#             recipient_list=[artist.email],
#         )

#         return JsonResponse({"status": "success", "message": "Booking successfully created and confirmation email sent!"})

#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})

# from datetime import datetime, timedelta

# @login_required
# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         date_selected = request.POST.get("date")
#         start_time_str = request.POST.get("start_time")
#         service_id = request.POST.get("service")
#         payment_method = request.POST.get("payment_method")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")

#         if not all([date_selected, start_time_str, service_id, payment_method]):
#             return JsonResponse({"status": "error", "message": "Missing required fields."})

#         try:
#             start_time = datetime.strptime(start_time_str, "%H:%M").time()
#         except ValueError:
#             return JsonResponse({"status": "error", "message": "Invalid time format. Please use HH:MM."})

#         # Get service
#         service = get_object_or_404(Service, id=service_id)

#         # ✅ Convert duration to minutes correctly
#         if isinstance(service.duration, timedelta):
#             service_duration_minutes = service.duration.total_seconds() // 60  # Convert to minutes
#         else:
#             service_duration_minutes = int(service.duration)  # If stored as integer

#         # ✅ Calculate end_time correctly
#         end_datetime = datetime.combine(datetime.today(), start_time) + timedelta(minutes=service_duration_minutes)
#         end_time = end_datetime.time()

#         # ✅ Prevent overlapping bookings
#         overlapping_booking = Booking.objects.filter(
#             artist=artist,
#             date=date_selected,
#             start_time__lte=end_time,
#             end_time__gte=start_time
#         ).exists()

#         if overlapping_booking:
#             return JsonResponse({"status": "error", "message": "The selected time slot is already booked. Please choose another time."})

#         # ✅ Create and save the booking
#         booking = Booking.objects.create(
#             artist=artist,
#             client=user,
#             service=service,
#             date=date_selected,
#             start_time=start_time,
#             end_time=end_time,
#             payment_method=payment_method,
#             latitude=latitude,
#             longitude=longitude
#         )

#         return JsonResponse({"status": "success", "message": "Booking successfully created!"})

#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})

# from datetime import datetime, timedelta
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Booking, Service, User

# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id)
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         service_id = request.POST.get("service")
#         date_str = request.POST.get("date")
#         start_time_str = request.POST.get("start_time")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")
#         payment_method = request.POST.get("payment_method")

#         service = get_object_or_404(Service, id=service_id)

#         # Convert date and time strings to Python datetime objects
#         date = datetime.strptime(date_str, "%Y-%m-%d").date()
#         start_time = datetime.strptime(start_time_str, "%H:%M").time()

#         # ✅ Calculate End Time (Including Service Duration + Travel Time)
#         start_datetime = datetime.combine(date, start_time)
#         total_minutes = int(service.duration.total_seconds() / 60) + int(service.travel_time.total_seconds() / 60)
#         end_datetime = start_datetime + timedelta(minutes=total_minutes)
#         end_time = end_datetime.time()  # Extract only the time

#         # ✅ Save booking with calculated end_time
#         booking = Booking.objects.create(
#             artist=artist,
#             client=request.user,
#             service=service,
#             date=date,
#             start_time=start_time,
#             end_time=end_time,  # ✅ Save calculated end_time
#             latitude=latitude if latitude else None,
#             longitude=longitude if longitude else None,
#             payment_method=payment_method,
#         )
#         messages.success(request, "Booking successfully created!")
#         return redirect("booking_history")  # Redirect to booking history page

#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})

# from datetime import datetime, timedelta
# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from django.db.models import Q  # ✅ Import Q for filtering overlapping bookings
# from .models import Booking, Service, User

# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id)
#     services = Service.objects.filter(artist=artist)

#     if request.method == "POST":
#         service_id = request.POST.get("service")
#         date_str = request.POST.get("date")
#         start_time_str = request.POST.get("start_time")
#         latitude = request.POST.get("latitude")
#         longitude = request.POST.get("longitude")
#         payment_method = request.POST.get("payment_method")

#         service = get_object_or_404(Service, id=service_id)

#         # Convert date and time strings to Python datetime objects
#         date = datetime.strptime(date_str, "%Y-%m-%d").date()
#         start_time = datetime.strptime(start_time_str, "%H:%M").time()

#         # ✅ Calculate End Time (Including Service Duration + Travel Time)
#         start_datetime = datetime.combine(date, start_time)
#         total_minutes = int(service.duration.total_seconds() / 60) + int(service.travel_time.total_seconds() / 60)
#         end_datetime = start_datetime + timedelta(minutes=total_minutes)
#         end_time = end_datetime.time()  # Extract only the time

#         # ✅ Check for existing overlapping bookings
#         existing_bookings = Booking.objects.filter(
#             artist=artist,
#             date=date
#         ).filter(
#             Q(start_time__lt=end_time, end_time__gt=start_time)  # ✅ Check for time conflicts
#         )

#         if existing_bookings.exists():
#             messages.error(request, "This time slot is already booked. Please select a different time.")
#             return redirect("book_artist", artist_id=artist_id)

#         # ✅ Save booking with calculated end_time
#         booking = Booking.objects.create(
#             artist=artist,
#             client=request.user,
#             service=service,
#             date=date,
#             start_time=start_time,
#             end_time=end_time,  # ✅ Save calculated end_time
#             latitude=latitude if latitude else None,
#             longitude=longitude if longitude else None,
#             payment_method=payment_method,
#         )
#         messages.success(request, "Booking successfully created!")
#         return redirect("booking_history")  # Redirect to booking history page

#     return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse  # ✅ Import JsonResponse for AJAX
from django.db.models import Q
from django.core.mail import send_mail  # ✅ Import send_mail
from django.conf import settings  # ✅ Import settings for email
from .models import Booking, Service, User

def book_artist(request, artist_id):
    artist = get_object_or_404(User, id=artist_id)
    services = Service.objects.filter(artist=artist)

    if request.method == "POST":
        service_id = request.POST.get("service")
        date_str = request.POST.get("date")
        start_time_str = request.POST.get("start_time")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        payment_method = request.POST.get("payment_method")

        service = get_object_or_404(Service, id=service_id)

        # Convert date and time strings to Python datetime objects
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_time = datetime.strptime(start_time_str, "%H:%M").time()

        # ✅ Calculate End Time (Including Service Duration + Travel Time)
        start_datetime = datetime.combine(date, start_time)
        total_minutes = int(service.duration.total_seconds() / 60) + int(service.travel_time.total_seconds() / 60)
        end_datetime = start_datetime + timedelta(minutes=total_minutes)
        end_time = end_datetime.time()  # Extract only the time

        # ✅ Check for existing overlapping bookings
        existing_bookings = Booking.objects.filter(
            artist=artist,
            date=date,
        ).filter(
            Q(start_time__lt=end_time, end_time__gt=start_time)  # Check for time conflicts
        )

        if existing_bookings.exists():
            return JsonResponse({"error": "This time slot is already booked. Please select a different time."}, status=400)

        # ✅ Save booking with calculated end_time
        booking = Booking.objects.create(
            artist=artist,
            client=request.user,
            service=service,
            date=date,
            start_time=start_time,
            end_time=end_time,  # ✅ Save calculated end_time
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None,
            payment_method=payment_method,
        )

        # ✅ Send confirmation email to the user
        subject = "Booking Confirmation - ArtistFinder"
        message = f"""
        Hello {request.user.first_name},

        Your booking has been successfully created!

        📌 Booking Details:
        - Artist: {artist.first_name} {artist.last_name}
        - Service: {service.service_name}
        - Date: {date}
        - Time: {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}
        - Payment Method: {payment_method}

        Thank you for booking with ArtistFinder!
        """
        from_email = settings.DEFAULT_FROM_EMAIL  # Use your configured email
        recipient_list = [request.user.email]

        try:
            send_mail(subject, message, from_email, recipient_list)
        except Exception as e:
            print(f"Email sending failed: {e}")  # Debugging in case of email failure

        return JsonResponse({"success": "Booking successfully created! A confirmation email has been sent."}, status=200)

    return render(request, "accounts/book_artist.html", {"artist": artist, "services": services})


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

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
@csrf_exempt
def update_booking_status(request, booking_id):
    """ Allows an artist to confirm or cancel a booking and send email notifications. """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            new_status = data.get("status")
            booking = get_object_or_404(Booking, id=booking_id)

            # ✅ Ensure only the assigned artist can update the booking
            if request.user != booking.artist:
                return JsonResponse({"success": False, "error": "Only the assigned artist can update this booking."}, status=403)

            # ✅ Update the booking status
            booking.status = new_status
            booking.save()

            # ✅ Construct email details
            subject = f"Booking {new_status}: {booking.service.service_name}"
            message = f"""
                Hello {booking.client.first_name},

                Your booking for {booking.service.service_name} with {booking.artist.first_name} {booking.artist.last_name} has been {new_status.lower()}.

                Booking Details:
                - Service: {booking.service.service_name}
                - Artist: {booking.artist.first_name} {booking.artist.last_name}
                - Date: {booking.date}
                - Time: {booking.time}
                - Payment Method: {booking.payment_method}
                - Price: ${booking.service.price}

                If you have any questions, please contact the artist at {booking.artist.email}.

                Best regards,
                Artist Finder Team
            """

            # ✅ Send email to client
            send_mail(
                subject,
                message,
                "no-reply@artistfinder.com",
                [booking.client.email],
                fail_silently=False,
            )

            # ✅ Send email to artist as well
            send_mail(
                f"Booking {new_status} - {booking.client.first_name}",
                f"Hello {booking.artist.first_name},\n\nYou have {new_status.lower()} a booking.\n\n{message}",
                "no-reply@artistfinder.com",
                [booking.artist.email],
                fail_silently=False,
            )

            return JsonResponse({
                "success": True,
                "message": f"Booking has been {new_status.lower()}!",
                "status": booking.status
            })

        except Booking.DoesNotExist:
            return JsonResponse({"success": False, "error": "Booking not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON request"}, status=400)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=400)





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








@login_required
def add_review(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)

    # ✅ Get only services booked by the user for this artist
    booked_services = Service.objects.filter(
        booking__client=request.user, booking__artist=artist, booking__status="Confirmed"
    ).distinct()

    if not booked_services.exists():
        messages.error(request, "You can only review services you've booked and confirmed.")
        return redirect('home')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        service_id = request.POST.get("service")  # ✅ Get the service ID from the form

        if not service_id:
            messages.error(request, "Please select a valid service.")
            return redirect(request.path)

        service = get_object_or_404(Service, id=service_id)

        if service not in booked_services:  # ✅ Ensure the service is valid
            messages.error(request, "You can only review services you have booked.")
            return redirect(request.path)

        if form.is_valid():
            review = form.save(commit=False)
            review.artist = artist
            review.user = request.user
            review.service = service  # ✅ Assign the valid service
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
from .forms import ServiceForm
from .models import Service
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def add_service(request):
    if request.method == "POST":
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.artist = request.user
            service.save()
            messages.success(request, "Service added successfully!")
            return redirect('services')
    else:
        form = ServiceForm()

    return render(request, 'accounts/add_service.html', {'form': form})


# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from .models import Service, ServiceAvailability

# @login_required
# def service_schedule(request):
#     services = Service.objects.all()  # Fetch all available services
#     return render(request, 'accounts/service_schedule.html', {'services': services})


# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Service, ServiceSchedule
# from .forms import ServiceScheduleForm
# from datetime import datetime, timedelta

# @login_required
# def service_schedule(request):
#     services = Service.objects.all()
#     schedules = ServiceSchedule.objects.all()

#     if request.method == "POST":
#         form = ServiceScheduleForm(request.POST)
#         if form.is_valid():
#             service = form.cleaned_data['service']
#             start_time = form.cleaned_data['start_time']

#             # Convert start time to datetime object for calculations
#             total_duration = service.total_duration
#             start_datetime = datetime.strptime(str(start_time), "%H:%M:%S")
#             end_datetime = start_datetime + total_duration

#             # Save schedule in database
#             ServiceSchedule.objects.create(
#                 service=service,
#                 start_time=start_datetime.time(),
#                 end_time=end_datetime.time()
#             )

#             messages.success(request, "Service schedule added successfully!")
#             return redirect('service_schedule')

#     else:
#         form = ServiceScheduleForm()

#     return render(request, 'accounts/service_schedule.html', {
#         'services': services,
#         'schedules': schedules,
#         'form': form
#     })
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, ServiceSchedule
from .forms import ServiceScheduleForm
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, ServiceSchedule
from .forms import ServiceScheduleForm
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, ServiceSchedule
from .forms import ServiceScheduleForm
from datetime import datetime, timedelta

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Service, ServiceSchedule
from .forms import ServiceScheduleForm
from datetime import datetime, timedelta

@login_required
def service_schedule(request):
    services = Service.objects.all()
    schedules = ServiceSchedule.objects.all()

    if request.method == "POST":
        form = ServiceScheduleForm(request.POST)
        if form.is_valid():
            service = form.cleaned_data['service']
            start_time = form.cleaned_data['start_time']

            # Convert start time to datetime object for calculations
            total_duration = service.total_duration
            start_datetime = datetime.strptime(str(start_time), "%H:%M:%S")
            end_datetime = start_datetime + total_duration

            # Loop through all workdays and create schedules
            for weekday in service.work_days:
                existing_schedules = ServiceSchedule.objects.filter(
                    service=service,
                    weekday=weekday,
                    start_time__lt=end_datetime.time(),
                    end_time__gt=start_time
                )

                if existing_schedules.exists():
                    messages.error(request, f"Another service is already scheduled at this time on {weekday}.")
                    return redirect('service_schedule')

                # ✅ Create schedule for each workday
                ServiceSchedule.objects.create(
                    service=service,
                    weekday=weekday,
                    start_time=start_datetime.time(),
                    end_time=end_datetime.time()
                )

            messages.success(request, f"Service schedule added successfully for {', '.join(service.work_days)}!")
            return redirect('service_schedule')

    else:
        form = ServiceScheduleForm()

    return render(request, 'accounts/service_schedule.html', {
        'services': services,
        'schedules': schedules,
        'form': form
    })



from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ServiceSchedule

def delete_schedule(request, schedule_id):
    schedule = get_object_or_404(ServiceSchedule, id=schedule_id)
    schedule.delete()
    messages.success(request, "Schedule removed successfully!")
    return redirect('service_schedule')





from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def get_notifications(request):
    user = request.user

    # Count new bookings for the logged-in artist
    new_bookings = Booking.objects.filter(artist=user, status="Pending").count()

    return JsonResponse({
        "new_bookings": new_bookings
    })


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Booking

@login_required
def mark_notifications_read(request):
    """
    This function should not automatically mark all 'Pending' bookings as 'Notified.'
    Instead, it will only return the count of 'Pending' bookings to show notifications.
    """
    user = request.user
    # Get the count of 'Pending' bookings (no status change)
    new_bookings = Booking.objects.filter(artist=user, status="Pending").count()

    return JsonResponse({"new_bookings": new_bookings})

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
