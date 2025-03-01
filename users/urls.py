from django.contrib.auth.views import PasswordResetConfirmView
from django.urls import path
from users.views.auth import *
from .views_ import download_book, request_book, get_users_ids
from users.views.passwords_view import *

urlpatterns = [
    path('register/', registration_view, name='register'),
    path("register/faceid/", face_register_view, name="face_register"),
    path('login/', login_view, name='login'),
    path("login/faceid/", face_login_view, name="face_login"),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/change/', user_update, name='user_update'),
    path('download/<int:book_id>/', download_book, name='download'),
    path('request/<int:book_id>/', request_book, name='request'),
    path('change/', account_edit_view, name='change'),
    path('downloads/', downloads_view, name='downloads'),
    path('requests/', requests_view, name='requests'),
    path('history/', history, name="history"),
    path('verify/', email_verify_view, name='email_verify'),
    path('password/change/', change_password, name='change_password'),
    path('password/reset/', password_reset, name='password_reset'),
    path('password/reset/done/', password_reset_done, name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('users/', get_users_ids, name='get_users_ids'),

]
