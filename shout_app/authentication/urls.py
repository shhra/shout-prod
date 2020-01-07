from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from .views import LoginAPIView, EmailConfirmAPIView
from rest_auth.views import (LogoutView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView)
from rest_auth.registration.views import VerifyEmailView


urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='account_login'),
    path('api/logout/', LogoutView.as_view(), name='account_logout'),
    path('api/u/change_password', PasswordChangeView.as_view(), name='password_change_view'),
    path('api/u/reset_passowrd', PasswordResetView.as_view(), name='password_reset_view'),
    path('api/u/reset_confirm', PasswordResetConfirmView.as_view(), name='password_reset_confirm_view'),
    path('api/u/verify_email', VerifyEmailView.as_view(), name='account_verify'),
    url('confirm_email/(?P<key>[-:\w]+)/$', EmailConfirmAPIView.as_view(), name='account_confirm_email')

]
