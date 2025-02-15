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



# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import update_session_auth_hash
# from django.contrib import messages
# from .forms import ProfileUpdateForm
# from .models import User

# @login_required(login_url='artist_login')
# def artist_profile(request):
#     if request.session.get('user_type') != 'artist':  # ✅ Ensure only artists can access
#         return redirect('artist_login')

#     user = request.user  # ✅ Get logged-in artist

#     if request.method == 'POST':
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
#         if form.is_valid():
#             updated_user = form.save(commit=False)
            
#             # ✅ Only update password if a new password is provided
#             new_password = form.cleaned_data.get('password')
#             if new_password:
#                 updated_user.set_password(new_password)
#                 update_session_auth_hash(request, updated_user)  # ✅ Keep user logged in
            
#             updated_user.save()
#             messages.success(request, "Profile updated successfully!")
#             return redirect('artist_profile')

#         else:
#             messages.error(request, "Please correct the errors in the form.")

#     else:
#         form = ProfileUpdateForm(instance=user)

#     return render(request, 'accounts/artist_profile.html', {
#         'form': form,
#         'artist': user  # ✅ Pass artist-specific data
#     })



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

                login(request, user)
                request.session['user_type'] = 'artist'  # Store artist separately
                return redirect('artist_dashboard')

            else:
                form.add_error(None, 'Invalid email or password.')

    return render(request, "accounts/artist_login.html", {'form': LoginForm()})




# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator
# from django.db.models import Avg
# from .models import User, Booking

# @login_required(login_url='login')
# def home_page(request):
#     query = request.GET.get("search", "").strip()
#     sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

#     # ✅ Filter artists based on search query (city)
#     artists = User.objects.filter(is_artist=True)
#     if query:
#         artists = artists.filter(city__icontains=query)

#     # ✅ Annotate artists with their average rating (FIXED FIELD NAME)
#     artists = artists.annotate(avg_rating=Avg('artist_reviews__rating'))  # Use correct related name

#     # ✅ Sorting logic
#     if sort_by == "rating":
#         artists = artists.order_by('-avg_rating')  # Highest rating first
#     elif sort_by == "name":
#         artists = artists.order_by('first_name', 'last_name')  # Alphabetical
#     elif sort_by == "experience":
#         artists = artists.order_by('-experience_years')  # Most experienced first

#     # ✅ Pagination (10 artists per page)
#     paginator = Paginator(artists, 10)  
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     # ✅ Fetch all artist IDs where the user has a confirmed booking
#     booked_artists = Booking.objects.filter(client=request.user, status="Confirmed").values_list('artist_id', flat=True)

#     return render(request, "accounts/home.html", {
#         "artists": page_obj,  # Paginated artists
#         "query": query,
#         "message": "No artists found in this city." if not artists.exists() else "",
#         "booked_artists": list(booked_artists),  # Convert to list
#         "sort_by": sort_by,
#     })
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from .models import User, Booking

@login_required(login_url='login')
def home_page(request):
    query = request.GET.get("search", "").strip()
    sort_by = request.GET.get("sort_by", "rating")  # Default sorting by rating

    # ✅ Filter artists based on search query (city)
    artists = User.objects.filter(is_artist=True)
    if query:
        artists = artists.filter(city__icontains=query)

    # ✅ Annotate artists with their average rating
    artists = artists.annotate(avg_rating=Avg('artist_reviews__rating'))

    # ✅ Sorting logic
    if sort_by == "rating":
        artists = artists.order_by('-avg_rating')  # Highest rating first
    elif sort_by == "name":
        artists = artists.order_by('first_name', 'last_name')  # Alphabetical
    elif sort_by == "experience":
        artists = artists.order_by('-experience_years')  # Most experienced first

    # ✅ Pagination (10 artists per page)
    paginator = Paginator(artists, 10)  
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ✅ Fetch all artist IDs where the user has a confirmed booking
    booked_artists = Booking.objects.filter(client=request.user, status="Confirmed").values_list('artist_id', flat=True)

    # ✅ AI-BASED RECOMMENDATION LOGIC
    # ✅ Find other users who booked the same artists as this user
    similar_users = Booking.objects.filter(artist_id__in=booked_artists).values_list("client_id", flat=True).distinct()

    # ✅ Find new artists booked by similar users but NOT booked by the current user
    recommended_artists = User.objects.filter(
        is_artist=True, 
        bookings__client_id__in=similar_users
    ).exclude(id__in=booked_artists).annotate(
        booking_count=Count("bookings")
    ).order_by("-booking_count")[:5]  # ✅ Top 5 recommended artists

    return render(request, "accounts/home.html", {
        "artists": page_obj,  # Paginated artists
        "recommended_artists": recommended_artists,  # ✅ Pass recommended artists
        "query": query,
        "message": "No artists found in this city." if not artists.exists() else "",
        "booked_artists": list(booked_artists),
        "sort_by": sort_by,
    })

# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Booking

# @login_required
# def cancel_booking(request, booking_id):
#     booking = get_object_or_404(Booking, id=booking_id, client=request.user)

#     if booking.status in ["Confirmed", "Pending"]:  # ✅ Allow cancelling both statuses
#         booking.status = "Cancelled"
#         booking.save()
#         messages.success(request, "Your booking has been successfully cancelled.")

#     return redirect("booking_history")  # ✅ Redirect user to their booking history


# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.http import JsonResponse
# from .models import Booking, ServiceAvailability

# @login_required
# def cancel_booking(request, booking_id):
#     """ Cancel a booking and make the time slot available again """
#     booking = get_object_or_404(Booking, id=booking_id, client=request.user)

#     if booking.status in ["Pending", "Confirmed"]:
#         # ✅ Mark the time slot as available again
#         ServiceAvailability.objects.filter(
#             service=booking.service,
#             available_date=booking.date,
#             available_time=booking.time
#         ).update(is_booked=False)  # Mark the slot as available

#         booking.status = "Cancelled"
#         booking.save()
#         messages.success(request, "Your booking has been canceled. The slot is now available.")

#         # ✅ Return JSON response for AJAX update
#         return JsonResponse({"success": True, "message": "Booking canceled and slot is now available."})

#     return JsonResponse({"success": False, "message": "Cannot cancel this booking."}, status=400)

# from django.shortcuts import get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.http import JsonResponse
# from .models import Booking, ServiceAvailability

# @login_required
# def cancel_booking(request, booking_id):
#     """ ✅ Cancel a booking and make the time slot available again """
#     booking = get_object_or_404(Booking, id=booking_id, client=request.user)

#     if booking.status in ["Pending", "Confirmed"]:
#         # ✅ Find the slot for this booking
#         slot = ServiceAvailability.objects.filter(
#             service=booking.service,
#             available_date=booking.date,
#             available_time=booking.time
#         ).first()

#         if slot:
#             slot.is_booked = False  # ✅ Mark as available
#             slot.save()  # ✅ Save changes to database

#         booking.status = "Cancelled"
#         booking.save()

#         messages.success(request, "Your booking has been canceled. The slot is now available.")

#         return JsonResponse({
#             "success": True,
#             "message": "Booking canceled and slot is now available.",
#             "service_id": booking.service.id,
#             "date": booking.date.strftime("%Y-%m-%d")  # ✅ Send date as string
#         })

#     return JsonResponse({"success": False, "message": "Cannot cancel this booking."}, status=400)
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Booking, ServiceAvailability

@login_required
def cancel_booking(request, booking_id):
    """ ✅ Cancel a booking and make the time slot available again """
    booking = get_object_or_404(Booking, id=booking_id, client=request.user)

    if booking.status in ["Pending", "Confirmed"]:
        # ✅ Find the corresponding service slot
        slot = ServiceAvailability.objects.filter(
            service=booking.service,
            available_date=booking.date,
            available_time=booking.time
        ).first()

        if slot:
            slot.is_booked = False  # ✅ Mark the slot as available again
            slot.save()
            print(f"✅ Slot {booking.time} on {booking.date} is now available again.")  # Debugging

        # ✅ Update booking status
        booking.status = "Cancelled"
        booking.save()
        print(f"✅ Booking {booking.id} successfully cancelled.")  # Debugging

        messages.success(request, "Your booking has been canceled. The slot is now available.")

        return JsonResponse({
            "success": True,
            "message": "Booking canceled and slot is now available.",
            "booking_id": booking.id,
            "service_id": booking.service.id,
            "date": booking.date.strftime("%Y-%m-%d")
        })

    return JsonResponse({"success": False, "message": "Cannot cancel this booking."}, status=400)



# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.forms import modelformset_factory
# from .models import Service, ServiceAvailability
# from .forms import ServiceForm, ServiceAvailabilityForm

# @login_required
# def edit_service(request, service_id):
#     service = get_object_or_404(Service, id=service_id, artist=request.user)

#     ServiceAvailabilityFormSet = modelformset_factory(
#         ServiceAvailability, 
#         form=ServiceAvailabilityForm, 
#         extra=1,  
#         can_delete=True  
#     )

#     if request.method == "POST":
#         service_form = ServiceForm(request.POST, instance=service)
#         availability_formset = ServiceAvailabilityFormSet(request.POST, queryset=ServiceAvailability.objects.filter(service=service))

#         if service_form.is_valid() and availability_formset.is_valid():
#             service = service_form.save()

#             for form in availability_formset:
#                 if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
#                     availability = form.save(commit=False)
#                     availability.service = service
#                     if availability.id is None:  # ✅ Save only new entries
#                         availability.save()

#             for form in availability_formset.deleted_forms:
#                 if form.instance.id is not None:  # ✅ Ensure instance exists before deleting
#                     form.instance.delete()

#             return redirect("services")

#     else:
#         service_form = ServiceForm(instance=service)
#         availability_formset = ServiceAvailabilityFormSet(queryset=ServiceAvailability.objects.filter(service=service))

#     return render(request, "accounts/edit_service.html", {
#         "service_form": service_form,
#         "availability_formset": availability_formset,
#     })



# from django.shortcuts import render, get_object_or_404, redirect
# from django.forms import modelformset_factory
# from .models import Service, ServiceAvailability
# from .forms import ServiceForm, ServiceAvailabilityForm

# def edit_service(request, service_id):
#     service = get_object_or_404(Service, id=service_id)

#     # ✅ Allow adding extra slots but don't show them by default
#     ServiceAvailabilityFormSet = modelformset_factory(
#         ServiceAvailability, 
#         form=ServiceAvailabilityForm, 
#         extra=0,  # ✅ Prevents empty default forms
#         can_delete=True
#     )

#     if request.method == "POST":
#         service_form = ServiceForm(request.POST, instance=service)
#         formset = ServiceAvailabilityFormSet(request.POST)

#         if service_form.is_valid() and formset.is_valid():
#             service_form.save()

#             # ✅ Save valid availability slots
#             instances = formset.save(commit=False)
#             for instance in instances:
#                 instance.service = service  # ✅ Assign the service before saving
#                 instance.save()

#             # ✅ Delete removed slots
#             for obj in formset.deleted_objects:
#                 obj.delete()

#             return redirect("services")  # ✅ Redirect after updating

#     else:
#         service_form = ServiceForm(instance=service)

#         # ✅ Only fetch existing availability slots
#         formset = ServiceAvailabilityFormSet(queryset=ServiceAvailability.objects.filter(service=service))

#     return render(request, "accounts/edit_service.html", {
#         "service_form": service_form,
#         "availability_formset": formset,
#     })
# from django.shortcuts import render, get_object_or_404, redirect
# from django.forms import modelformset_factory
# from .models import Service, ServiceAvailability
# from .forms import ServiceForm, ServiceAvailabilityForm

# def edit_service(request, service_id):
#     service = get_object_or_404(Service, id=service_id)

#     ServiceAvailabilityFormSet = modelformset_factory(
#         ServiceAvailability, 
#         form=ServiceAvailabilityForm, 
#         extra=1,  # ✅ Allow adding extra slot
#         can_delete=True  # ✅ Allow removing slots
#     )

#     if request.method == "POST":
#         service_form = ServiceForm(request.POST, instance=service)
#         formset = ServiceAvailabilityFormSet(request.POST, queryset=ServiceAvailability.objects.filter(service=service))

#         if service_form.is_valid() and formset.is_valid():
#             service = service_form.save()

#             for form in formset:
#                 if form.cleaned_data and not form.cleaned_data.get("DELETE", False):
#                     availability = form.save(commit=False)
#                     availability.service = service
#                     availability.save()

#             for form in formset.deleted_forms:
#                 if form.instance.pk:
#                     form.instance.delete()

#             return redirect("services")

#     else:
#         service_form = ServiceForm(instance=service)
#         formset = ServiceAvailabilityFormSet(queryset=ServiceAvailability.objects.filter(service=service))

#     return render(request, "accounts/edit_service.html", {
#         "service_form": service_form,
#         "availability_formset": formset,
#     })
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


# ✅ Artist Registration (Fully Fixed)
def register_artists(request):
    if request.method == "POST":
        form = ArtistRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            otp = str(random.randint(100000, 999999))
            user = form.save(commit=False)

            # ✅ Ensure password is hashed properly
            if form.cleaned_data.get('password'):
                user.password = make_password(form.cleaned_data['password'])

            user.is_artist = True  
            user.is_verified = False  
            user.otp = otp  
            user.save()

            send_mail(
                'Your OTP for Artist Registration', 
                f'Your OTP is {otp}', 
                'admin@artistfinder.com', 
                [user.email]
            )

            request.session['user_id'] = user.id
            return redirect('verify_otp')

    return render(request, 'accounts/register_artists.html', {'form': ArtistRegisterForm()})

# ✅ Artist Dashboard
@login_required(login_url='artist_login')
def artist_dashboard(request):
    artist = request.user
    if not artist.is_artist:
        return redirect('artist_login')

    works = Work.objects.filter(artist=artist)
    return render(request, 'accounts/artist_dashboard.html', {'works': works})

# # ✅ Artist Logout (Fully Fixed)
# def artist_logout(request):
#     logout(request)  # ✅ Clears session but NOT password
#     return redirect('artist_login')  # ✅ Redirect to login page
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

@login_required(login_url='artist_login')
def services(request):
    artist_services = Service.objects.filter(artist=request.user).prefetch_related('service_reviews')  # ✅ Load reviews efficiently
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
#             service = service_form.save(commit=False)
#             service.artist = request.user  # Assign artist before saving
#             service.save()

#             # ✅ Ensure all slots are saved correctly
#             availabilities = formset.save(commit=False)
#             for availability in availabilities:
#                 availability.service = service
#                 availability.save()

#             return redirect('services')  # Redirect after successful submission

#     else:
#         service_form = ServiceForm()
#         formset = ServiceAvailabilityFormSet()

#     return render(request, 'accounts/add_service.html', {
#         'service_form': service_form,
#         'formset': formset
#     })



from django.shortcuts import render, redirect
from .models import Service, ServiceAvailability
from .forms import ServiceForm, ServiceAvailabilityFormSet
from django.contrib.auth.decorators import login_required

@login_required
def add_service(request):
    if request.method == "POST":
        service_form = ServiceForm(request.POST)
        formset = ServiceAvailabilityFormSet(request.POST)

        if service_form.is_valid() and formset.is_valid():
            # ✅ Create and Save the Service First
            service = service_form.save(commit=False)
            service.artist = request.user  # Assign artist before saving
            service.save()

            # ✅ Save all availability slots related to the service
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    availability = form.save(commit=False)
                    availability.service = service  # Link to service
                    availability.save()

            return redirect('services')  # Redirect to services page

    else:
        service_form = ServiceForm()
        formset = ServiceAvailabilityFormSet(queryset=ServiceAvailability.objects.none())  # Empty formset

    return render(request, 'accounts/add_service.html', {
        'service_form': service_form,
        'formset': formset
    })




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Booking, ServiceAvailability, User

def get_available_slots(request, artist_id):
    selected_date = request.GET.get("date")
    artist = get_object_or_404(User, id=artist_id)

    if not selected_date:
        return JsonResponse({"error": "Invalid date selected"}, status=400)

    # ✅ Get all booked slots for this artist and date
    booked_slots = Booking.objects.filter(artist=artist, date=selected_date).values_list("time", flat=True)

    # ✅ Get only the available time slots set by the artist for this date
    available_slots = ServiceAvailability.objects.filter(
        service__artist=artist, available_date=selected_date
    ).values_list("available_time", flat=True)

    # ✅ Convert to a list of time strings
    booked_times = [time.strftime("%H:%M") for time in booked_slots]
    artist_defined_times = [time.strftime("%H:%M") for time in available_slots]

    # ✅ Show only available slots that are not booked
    final_slots = [time for time in artist_defined_times if time not in booked_times]

    return JsonResponse({"available_times": final_slots})


# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import ServiceAvailability, User

# def get_available_dates(request, artist_id):
#     """ ✅ Fetch only available dates for the artist """
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)

#     # ✅ Get unique available dates
#     available_dates = ServiceAvailability.objects.filter(
#         service__artist=artist
#     ).values_list("available_date", flat=True).distinct()

#     # ✅ Convert dates to string format (YYYY-MM-DD) for JavaScript
#     available_dates = [date.strftime("%Y-%m-%d") for date in available_dates]

#     return JsonResponse({"available_dates": available_dates})




# def get_available_times(request, artist_id):
#     """ ✅ Fetch only available times for the selected date """
#     selected_date = request.GET.get("date")
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)

#     if not selected_date:
#         return JsonResponse({"error": "Invalid date selected"}, status=400)

#     # ✅ Get available time slots for this date
#     available_slots = ServiceAvailability.objects.filter(
#         service__artist=artist, available_date=selected_date
#     ).values_list("available_time", flat=True)

#     # ✅ Convert time to string format (HH:MM)
#     available_times = [time.strftime("%H:%M") for time in available_slots]

#     return JsonResponse({"available_times": available_times})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ServiceAvailability, Service

def get_available_dates(request, artist_id):
    """ ✅ Fetch only available dates for the selected service """
    service_id = request.GET.get("service_id")  # ✅ Get selected service ID

    if not service_id:
        return JsonResponse({"error": "Service ID is required"}, status=400)

    service = get_object_or_404(Service, id=service_id, artist_id=artist_id)  # ✅ Ensure the service belongs to the artist

    # ✅ Get unique available dates for the selected service
    available_dates = ServiceAvailability.objects.filter(service=service).values_list("available_date", flat=True).distinct()

    # ✅ Convert dates to string format (YYYY-MM-DD) for JavaScript
    available_dates = [date.strftime("%Y-%m-%d") for date in available_dates]

    return JsonResponse({"available_dates": available_dates})

# def get_available_times(request, artist_id):
#     """ ✅ Fetch only available times for the selected date and service """
#     selected_date = request.GET.get("date")
#     service_id = request.GET.get("service_id")  # ✅ Get selected service ID

#     if not selected_date or not service_id:
#         return JsonResponse({"error": "Service ID and date are required"}, status=400)

#     service = get_object_or_404(Service, id=service_id, artist_id=artist_id)

#     # ✅ Get available time slots for this service & date
#     available_slots = ServiceAvailability.objects.filter(
#         service=service, available_date=selected_date
#     ).values_list("available_time", flat=True)

#     # ✅ Convert time to string format (HH:MM)
#     available_times = [time.strftime("%H:%M") for time in available_slots]

#     return JsonResponse({"available_times": available_times})

# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import ServiceAvailability, Service

# def get_available_times(request, artist_id):
#     """ ✅ Fetch only available times for the selected date and service """
#     selected_date = request.GET.get("date")
#     service_id = request.GET.get("service_id")  # ✅ Get selected service ID

#     if not selected_date or not service_id:
#         return JsonResponse({"error": "Service ID and date are required"}, status=400)

#     service = get_object_or_404(Service, id=service_id, artist_id=artist_id)

#     # ✅ Get available time slots that are NOT booked
#     available_slots = ServiceAvailability.objects.filter(
#         service=service, available_date=selected_date, is_booked=False
#     ).values_list("available_time", flat=True)

#     # ✅ Convert time to string format (HH:MM)
#     available_times = [time.strftime("%H:%M") for time in available_slots]

#     return JsonResponse({"available_times": available_times})
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import ServiceAvailability, Service

def get_available_times(request, artist_id):
    """ ✅ Fetch only available times for the selected date and service """
    selected_date = request.GET.get("date")
    service_id = request.GET.get("service_id")  # ✅ Get selected service ID

    if not selected_date or not service_id:
        return JsonResponse({"error": "Service ID and date are required"}, status=400)

    service = get_object_or_404(Service, id=service_id, artist_id=artist_id)

    # ✅ Get only available time slots (not booked)
    available_slots = ServiceAvailability.objects.filter(
        service=service, available_date=selected_date, is_booked=False
    ).values_list("available_time", flat=True)

    # ✅ Convert time to string format (HH:MM)
    available_times = [time.strftime("%H:%M") for time in available_slots]

    return JsonResponse({"available_times": available_times})



# from django.shortcuts import render
# from .models import User

# def artist_list(request):
#     artists = User.objects.filter(is_artist=True).prefetch_related('services')
#     return render(request, 'accounts/artist_list.html', {'artists': artists})


from django.shortcuts import render
from .models import User  # Assuming User model is used for artists

def artist_list(request):
    artists = User.objects.filter(is_artist=True)  # ✅ Only show users who are artists
    cities = User.objects.filter(is_artist=True).values_list('city', flat=True).distinct()  # ✅ Get cities for artists only
    return render(request, "accounts/artist_list.html", {"artists": artists, "cities": cities})







from django.shortcuts import render, get_object_or_404
from .models import User, Work

def artist_detail(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    works = Work.objects.filter(artist=artist)  # ✅ Fetch works related to the artist

    return render(request, 'accounts/artist_detail.html', {
        'artist': artist,
        'works': works
    })



# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import User

# @login_required
# def certificates_page(request):
#     user = request.user  # Get logged-in user

#     if request.method == "POST":
#         if "training_certificate" in request.FILES:
#             user.training_certificate = request.FILES["training_certificate"]
#             user.save()
#             messages.success(request, "Certificate uploaded successfully!")
#             return redirect("certificates")

#     return render(request, "accounts/certificates.html", {"user": user})


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








# from django.shortcuts import get_object_or_404
# from django.http import HttpResponse
# from django.utils.timezone import now
# from accounts.models import Booking, User, Service

# def khalti_request(request, amount, artist_id, user_id, service_id):
#     user = get_object_or_404(User, id=user_id)
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     service = get_object_or_404(Service, id=service_id)

#     # ✅ Create a booking WITHOUT 'amount' (service price is already in the Service model)
#     booking = Booking.objects.create(
#         client=user,
#         artist=artist,
#         service=service,
#         date=now(),  # ✅ Ensure a valid date is passed
#         time=now().time(),  # ✅ Set the time dynamically
#         payment_method="khalti",  # ✅ Assuming Khalti payment
#         payment_status="Pending",
#         status="Pending",
#         transaction_id=None  # ✅ Transaction will be added after payment
#     )

#     booking.save()

#     return HttpResponse(f"Booking successful for service: {service.service_name} at Rs. {service.price}")






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

#         # ✅ Save booking to the database
#         booking = Booking.objects.create(
#             artist=artist,
#             client=user,
#             date=date_selected,
#             time=time_selected,
#             service=selected_service,
#             payment_method=payment_method
#         )

#         # ✅ Handle Khalti Payment
#         if payment_method == "khalti":
#             total_amount = int(selected_service.price) * 100  # Convert to paisa
#             return JsonResponse({
#                 "status": "redirect",
#                 "url": f"/khalti-request/?amount={total_amount}&service_id={selected_service.id}&artist_id={artist.id}"
#             })

#         return JsonResponse({"status": "success", "message": "Booking confirmed!"})

#     return render(request, 'accounts/book_artist.html', {
#         'artist': artist,
#         'user': user,
#         'services': services
#     })


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
#         latitude = request.POST.get("latitude")  # ✅ Get latitude
#         longitude = request.POST.get("longitude")  # ✅ Get longitude

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
#             latitude=latitude,  # ✅ Save latitude
#             longitude=longitude,  # ✅ Save longitude
#         )

#         messages.success(request, "Your booking has been successfully listed. You will receive a confirmation message soon.")
#         return redirect("accounts/home.html")  # Redirect to a success page

#     return render(request, 'accounts/book_artist.html', {
#         'artist': artist,
#         'user': user,
#         'services': services
#     })
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from datetime import date
from .models import Booking, Service, User, ServiceAvailability

# Initialize logger
logger = logging.getLogger(__name__)

@login_required
def book_artist(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    user = request.user
    services = Service.objects.filter(artist=artist)

    if request.method == "POST":
        date_selected = request.POST.get("date")
        time_selected = request.POST.get("time")
        service_id = request.POST.get("service")
        payment_method = request.POST.get("payment_method")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        logger.info(f"Received booking request from {user.email} for {artist.first_name}")

        # ✅ Validate required fields
        if not date_selected or not time_selected or not service_id or not payment_method:
            return JsonResponse({"status": "error", "message": "All fields are required."})

        # ✅ Ensure selected date is not in the past
        if date.fromisoformat(date_selected) < date.today():
            return JsonResponse({"status": "error", "message": "You cannot book past dates."})

        selected_service = get_object_or_404(Service, id=service_id, artist=artist)

        # ✅ Ensure the selected time slot exists in ServiceAvailability
        if not ServiceAvailability.objects.filter(
            service=selected_service, available_date=date_selected, available_time=time_selected
        ).exists():
            return JsonResponse({"status": "error", "message": "The selected time slot is not available."})

        # ✅ Check if the artist is already booked at this date & time
        if Booking.objects.filter(artist=artist, date=date_selected, time=time_selected).exists():
            return JsonResponse({"status": "error", "message": "This time slot is already booked. Choose another."})

        # ✅ Save booking with latitude & longitude
        booking = Booking.objects.create(
            artist=artist,
            client=user,
            date=date_selected,
            time=time_selected,
            service=selected_service,
            payment_method=payment_method,
            latitude=latitude,
            longitude=longitude,
            status="Pending"  # ✅ Default to pending until confirmed
        )

        logger.info(f"Booking created successfully: {booking.id}")

        # ✅ Send confirmation email
        try:
            send_mail(
                "Booking Confirmation - Artist Finder",
                f"Dear {user.first_name},\n\nYour booking for {selected_service.service_name} with {artist.first_name} {artist.last_name} on {date_selected} at {time_selected} has been received.\n\nYou will get a confirmation mail soon!\n\nThank you for using Artist Finder!",
                "no-reply@artistfinder.com",
                [user.email],
                fail_silently=False,
            )
            logger.info("Confirmation email sent successfully!")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")

        return JsonResponse({
            "status": "success",
            "message": "Your booking has been listed. You will receive a confirmation message soon.",
        })

    return render(request, 'accounts/book_artist.html', {
        'artist': artist,
        'user': user,
        'services': services
    })


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






from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.contrib import messages
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




from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Booking, Notification

@login_required
def booking_history(request):
    # ✅ Fetch the user's bookings
    user_bookings = Booking.objects.filter(client=request.user).order_by("-date")

    # ✅ Fetch notifications for the user
    user_notifications = Notification.objects.filter(user=request.user).order_by("-created_at")

    # ✅ Mark notifications as read
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    return render(request, "accounts/booking_history.html", {
        "user_bookings": user_bookings,
        "notifications": user_notifications
    })



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








from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Review, Booking, Service
from .forms import ReviewForm

@login_required
def add_review(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)

    # ✅ Get only the services that the user has booked and confirmed
    booked_services = Service.objects.filter(
        booking__client=request.user, booking__artist=artist, booking__status="Confirmed"
    ).distinct()

    if not booked_services.exists():
        messages.error(request, "You can only review services you've booked and confirmed.")
        return redirect('home')

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.artist = artist
            review.user = request.user
            review.service = get_object_or_404(Service, id=request.POST.get("service"))
            review.save()
            messages.success(request, "Your review has been submitted successfully!")
            return redirect('home')  # Redirect to services page
    else:
        form = ReviewForm()

    return render(request, 'accounts/review_form.html', {
        'form': form,
        'artist': artist,
        'services': booked_services  # ✅ Pass only booked services
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



# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from .models import Service
# from .forms import ServiceForm

# @login_required
# def edit_service(request, service_id):
#     service = get_object_or_404(Service, id=service_id, artist=request.user)

#     if request.method == "POST":
#         form = ServiceForm(request.POST, instance=service)
#         if form.is_valid():
#             form.save()
#             return redirect("services")  # ✅ Redirect back to services page
#     else:
#         form = ServiceForm(instance=service)

#     return render(request, "accounts/edit_service.html", {"form": form, "service": service})


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


  