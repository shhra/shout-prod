from django.contrib import admin
from django.urls import path, include
from .views import LoginAPIView


urlpatterns = [
    path('api/login/', LoginAPIView.as_view(), name='login_view'),
]
