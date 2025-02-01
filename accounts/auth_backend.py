# from django.contrib.auth.backends import BaseBackend
# from django.contrib.auth.hashers import check_password
# from .models import User

# class EmailAuthBackend(BaseBackend):
#     """Custom authentication backend to log in using email instead of username."""

#     def authenticate(self, request, email=None, password=None, **kwargs):
#         try:
#             user = User.objects.get(email=email)
#             if check_password(password, user.password):  # ✅ Check password manually
#                 return user
#         except User.DoesNotExist:
#             return None

#     def get_user(self, user_id):
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None
