

# from django.contrib.auth.decorators import login_required
# from django.contrib.auth import update_session_auth_hash
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.hashers import make_password
# from .models import User
# from .forms import ProfileUpdateForm
# from django.contrib.auth import update_session_auth_hash

# @login_required(login_url='artist_login')
# def artist_profile(request):
#     user = request.user
    
#     if request.method == 'POST':
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        
#         if form.is_valid():
#             updated_user = form.save(commit=False)

#             # ✅ Preserve existing password
#             if not form.cleaned_data.get('password'):
#                 updated_user.password = user.password
#             else:
#                 updated_user.password = make_password(form.cleaned_data['password'])

#             updated_user.save()

#             # ✅ Prevent logout after profile update
#             update_session_auth_hash(request, updated_user)

#             return redirect('artist_profile')

#     return render(request, 'accounts/artist_profile.html', {'form': ProfileUpdateForm(instance=user)})









# from django.shortcuts import render, redirect, get_object_or_404
# from django.core.mail import send_mail
# from django.contrib.auth.hashers import make_password, check_password
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from .models import User, Work, Service
# from .forms import RegistrationForm, LoginForm, ProfileUpdateForm, ArtistRegisterForm, OTPForm, ServiceForm
# import random

# # ✅ Registration Page
# def register_page(request):
#     return render(request, 'accounts/register.html')

# # ✅ Handles Normal User Registration & OTP Verification
# def register_normal(request):
#     if request.method == 'POST':
#         form = RegistrationForm(request.POST, request.FILES)
#         if form.is_valid():
#             otp = str(random.randint(100000, 999999))
#             user = form.save(commit=False)
#             user.password = make_password(form.cleaned_data['password'])  
#             user.otp = otp
#             user.save()

#             # Send OTP
#             send_mail('Your OTP for Artist Finder', f'Your OTP is {otp}', 'admin@artistfinder.com', [user.email])

#             request.session['user_id'] = user.id  
#             return redirect('verify_otp')

#     else:
#         form = RegistrationForm()
    
#     return render(request, 'accounts/register_normal.html', {'form': form})

# # ✅ OTP Verification
# def verify_otp(request):
#     user_id = request.session.get('user_id')
#     if not user_id:
#         return redirect('register')

#     user = get_object_or_404(User, id=user_id)

#     if request.method == 'POST':
#         form = OTPForm(request.POST)
#         if form.is_valid() and form.cleaned_data['otp'] == user.otp:
#             user.is_verified = True
#             user.otp = None
#             user.save()

#             return redirect('artist_login' if user.is_artist else 'login')
#         else:
#             form.add_error('otp', 'Invalid OTP')

#     return render(request, 'accounts/verify_otp.html', {'form': OTPForm()})

# # ✅ User Login (Fixed to Use `authenticate`)
# def login_page(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = authenticate(request, email=email, password=password)  # ✅ Use Django authentication

#             if user is not None and not user.is_artist:
#                 login(request, user)  # ✅ Correct Django login
#                 return redirect('home')
#             else:
#                 form.add_error(None, 'Invalid email or password.')

#     return render(request, 'accounts/login.html', {'form': LoginForm()})

# def artist_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data['email']
#             password = form.cleaned_data['password']
#             user = authenticate(request, email=email, password=password)  # ✅ Use authenticate()

#             if user is not None and user.is_artist:
#                 if not user.is_verified:
#                     form.add_error(None, 'Account not verified. Please verify via OTP.')
#                 else:
#                     login(request, user)  # ✅ Django login
#                     return redirect('artist_dashboard')

#             form.add_error(None, 'Invalid email or password.')

#     return render(request, "accounts/artist_login.html", {'form': LoginForm()})


# # ✅ Home Page (Fixed)
# @login_required(login_url='login')
# def home_page(request):
#     return render(request, 'accounts/home.html', {'user': request.user})

# # ✅ User Profile (Fixed Password Preservation)
# @login_required(login_url='login')
# def user_profile(request):
#     user = request.user
#     if request.method == 'POST':
#         form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
#         if form.is_valid():
#             updated_user = form.save(commit=False)

#             # ✅ Preserve password if not updated
#             if not form.cleaned_data.get('password'):
#                 updated_user.password = user.password
#             else:
#                 updated_user.password = make_password(form.cleaned_data['password'])

#             updated_user.save()
#             return redirect('user_profile')

#     return render(request, 'accounts/profile.html', {'form': ProfileUpdateForm(instance=user)})

# def register_artists(request):
#     if request.method == "POST":
#         form = ArtistRegisterForm(request.POST, request.FILES)
#         if form.is_valid():
#             otp = str(random.randint(100000, 999999))
#             user = form.save(commit=False)

#             # ✅ Ensure password is hashed properly
#             if form.cleaned_data.get('password'):
#                 user.password = make_password(form.cleaned_data['password'])

#             user.is_artist = True  
#             user.is_verified = False  
#             user.otp = otp  
#             user.save()

#             send_mail('Your OTP for Artist Registration', f'Your OTP is {otp}', 'admin@artistfinder.com', [user.email])

#             request.session['user_id'] = user.id
#             return redirect('verify_otp')

#     return render(request, 'accounts/register_artists.html', {'form': ArtistRegisterForm()})


# # ✅ Artist Dashboard
# @login_required(login_url='artist_login')
# def artist_dashboard(request):
#     artist = request.user
#     if not artist.is_artist:
#         return redirect('artist_login')

#     works = Work.objects.filter(artist=artist)
#     return render(request, 'accounts/artist_dashboard.html', {'works': works})

# def artist_logout(request):
#     logout(request)  # ✅ Clears user session
#     request.session.flush()  # ✅ Clears all session data
#     return redirect('artist_login')


# # ✅ Add Work (Fixed)
# @login_required(login_url='artist_login')
# def add_work(request):
#     artist = request.user

#     if request.method == 'POST':
#         title = request.POST.get('title')
#         description = request.POST.get('description')
#         image = request.FILES.get('image')

#         if not title or not image:
#             return render(request, 'accounts/add_work.html', {'error': "Title and image are required."})

#         Work.objects.create(
#             artist=artist,
#             title=title,
#             description=description,
#             image=image
#         )

#         return redirect('artist_dashboard')

#     return render(request, 'accounts/add_work.html')

# # ✅ Services Page
# @login_required(login_url='artist_login')
# def services(request):
#     artist_services = Service.objects.filter(artist=request.user)
#     return render(request, 'accounts/services.html', {'services': artist_services})

# # ✅ Add Service (Fixed)
# @login_required(login_url='artist_login')
# def add_service(request):
#     if request.method == 'POST':
#         form = ServiceForm(request.POST)
#         if form.is_valid():
#             service = form.save(commit=False)
#             service.artist = request.user
#             service.save()
#             return redirect('services')
    
#     return render(request, 'accounts/add_service.html', {'form': ServiceForm()})






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

# ✅ Artist Profile (Fully Fixed)
@login_required(login_url='artist_login')
def artist_profile(request):
    user = request.user

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            updated_user = form.save(commit=False)

            # ✅ Preserve password if not changed
            new_password = form.cleaned_data.get('password')
            if new_password:
                updated_user.password = make_password(new_password)  # ✅ Hash new password
            else:
                updated_user.password = user.password  # ✅ Keep old password

            updated_user.save()
            update_session_auth_hash(request, updated_user)  # ✅ Prevent logout after update

            return redirect('artist_profile')

    return render(request, 'accounts/artist_profile.html', {'form': ProfileUpdateForm(instance=user)})

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

# ✅ User Login (Fully Fixed)
def login_page(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None and not user.is_artist:
                login(request, user)
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
            user = authenticate(request, email=email, password=password)  # ✅ Ensure correct authentication

            if user is None:
                form.add_error(None, 'Invalid email or password.')
                return render(request, "accounts/artist_login.html", {'form': form})

            if user.is_artist:
                if not user.is_verified:
                    form.add_error(None, 'Account not verified. Please verify via OTP.')
                    return render(request, "accounts/artist_login.html", {'form': form})

                login(request, user)  # ✅ Ensures user remains authenticated
                return redirect('artist_dashboard')

            else:
                form.add_error(None, 'Invalid email or password.')

    return render(request, "accounts/artist_login.html", {'form': LoginForm()})

# ✅ Home Page
@login_required(login_url='login')
def home_page(request):
   artists = User.objects.filter(is_artist=True)  # ✅ Fetch only artists
   return render(request, 'accounts/home.html', {'artists': artists})  #

# ✅ User Profile (Fully Fixed)
@login_required(login_url='login')
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            updated_user = form.save(commit=False)

            # ✅ Preserve password if not updated
            if not form.cleaned_data.get('password'):
                updated_user.password = user.password
            else:
                updated_user.password = make_password(form.cleaned_data['password'])

            updated_user.save()
            update_session_auth_hash(request, updated_user)
            return redirect('user_profile')

    return render(request, 'accounts/profile.html', {'form': ProfileUpdateForm(instance=user)})

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

# ✅ Artist Logout (Fully Fixed)
def artist_logout(request):
    logout(request)  # ✅ Clears session but NOT password
    return redirect('artist_login')  # ✅ Redirect to login page

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

# ✅ Services Page
@login_required(login_url='artist_login')
def services(request):
    artist_services = Service.objects.filter(artist=request.user)
    return render(request, 'accounts/services.html', {'services': artist_services})

# ✅ Add Service
@login_required(login_url='artist_login')
def add_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.artist = request.user
            service.save()
            return redirect('services')
    
    return render(request, 'accounts/add_service.html', {'form': ServiceForm()})


from django.shortcuts import render
from .models import User

def artist_list(request):
    artists = User.objects.filter(is_artist=True)  # ✅ Get all registered artists
    return render(request, 'accounts/artist_list.html', {'artists': artists})
from django.shortcuts import render
from .models import User

def home_page(request):
    artists = User.objects.filter(is_artist=True)  # ✅ Fetch registered artists
    return render(request, 'accounts/home.html', {'artists': artists})






from django.shortcuts import render, get_object_or_404
from .models import User, Work

def artist_detail(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    works = Work.objects.filter(artist=artist)  # ✅ Fetch works related to the artist

    return render(request, 'accounts/artist_detail.html', {
        'artist': artist,
        'works': works
    })



from django.shortcuts import render, get_object_or_404
from .models import User

def chat_with_artist(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    return render(request, 'accounts/chat.html', {'artist': artist})




from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, ChatMessage

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, ChatMessage

def user_chat(request, artist_id):
    """ Chat page for users messaging an artist """
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    messages = ChatMessage.objects.filter(sender=request.user, receiver=artist) | \
               ChatMessage.objects.filter(sender=artist, receiver=request.user)
    messages = messages.order_by('timestamp')
    
    return render(request, 'accounts/user_chat.html', {'artist': artist, 'messages': messages})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, ChatMessage

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import User, ChatMessage

def artist_chat(request):
    artist = request.user
    if not artist.is_artist:
        return JsonResponse({"error": "Only artists can access this page."}, status=403)

    messages = ChatMessage.objects.filter(receiver=artist) | ChatMessage.objects.filter(sender=artist)
    messages = messages.order_by('timestamp')

    # ✅ Define receiver_id properly
    if messages.exists():
        first_message = messages.first()
        receiver_id = first_message.sender.id if first_message.sender.id != request.user.id else first_message.receiver.id
    else:
        receiver_id = None  # No messages yet

    return render(request, 'accounts/artist_chat.html', {'messages': messages, 'receiver_id': receiver_id})

# ✅ Handle Message Sending (Allows Artists to Reply)
@csrf_exempt
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        sender = User.objects.get(id=data['sender_id'])
        receiver = User.objects.get(id=data['receiver_id'])
        message = data['message']

        chat_message = ChatMessage.objects.create(sender=sender, receiver=receiver, message=message)
        return JsonResponse({"status": "Message sent", "message": message})
    return JsonResponse({"error": "Invalid request"}, status=400)



def home_page(request):
    artists = User.objects.filter(is_artist=True)  # Get all artists
    return render(request, 'accounts/home.html', {'artists': artists})

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import Booking, Service

# def book_artist(request, artist_id):
#     artist = get_object_or_404(User, id=artist_id, is_artist=True)
#     user = request.user  # ✅ Get logged-in user details
#     services = Service.objects.filter(artist=artist)  # ✅ Fetch services for the artist

#     if request.method == "POST":
#         date = request.POST.get("date")
#         time = request.POST.get("time")
#         service_id = request.POST.get("service")  # ✅ Get selected service

#         selected_service = Service.objects.get(id=service_id)

#         # ✅ Save booking in the database
#         Booking.objects.create(
#             artist=artist,
#             client=user,
#             date=date,
#             time=time,
#             service=selected_service
#         )

#         messages.success(request, f"Booking confirmed with {artist.first_name} for {selected_service.service_name} on {date} at {time}!")
#         return redirect("artist_chat")

#     return render(request, 'accounts/book_artist.html', {
#         'artist': artist,
#         'user': user,
#         'services': services  # ✅ Send services to the template
#     })

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Booking, Service
from django.http import JsonResponse

def book_artist(request, artist_id):
    artist = get_object_or_404(User, id=artist_id, is_artist=True)
    user = request.user
    services = Service.objects.filter(artist=artist)

    if request.method == "POST":
        date = request.POST.get("date")
        time = request.POST.get("time")
        service_id = request.POST.get("service")
        payment_method = request.POST.get("payment_method")  # ✅ Get payment method

        if not service_id or not payment_method:
            messages.error(request, "Please select a service and a payment method.")
            return redirect('book_artist', artist_id=artist.id)

        selected_service = Service.objects.get(id=service_id)

        # ✅ Save booking with payment method
        Booking.objects.create(
            artist=artist,
            client=user,
            date=date,
            time=time,
            service=selected_service,
            payment_method=payment_method  # ✅ Store payment method
        )

        messages.success(request, f"Booking confirmed with {artist.first_name} for {selected_service.service_name} using {payment_method}!")
        
        # ✅ Handle Khalti Payment
        if payment_method == "khalti":
            return JsonResponse({"status": "redirect", "url": "/khalti-payment-url"})  # ✅ Redirect to Khalti payment
    
        return redirect("artist_chat")

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
