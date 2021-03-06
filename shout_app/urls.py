"""shout_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls import url
from django.views.generic.base import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, TokenVerifyView,
)
from rest_auth.registration.views import RegisterView
from shout_app.authentication.views import EmailConfirmAPIView

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    # path('admin/', admin.site.urls),
    path('', include('shout_app.authentication.urls')),
    path('', include('shout_app.profile.urls')),
    path('', include('shout_app.shouts.urls')),
    path('api/request-auth-token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/request-auth-token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/request-auth-token/verify', TokenVerifyView.as_view(), name='token_verify'),
    path('api/signup/', RegisterView.as_view(), name='account_signup'),
    url('confirm_email/(?P<key>[-:\w]+)/$', EmailConfirmAPIView.as_view(), name='account_confirm_email')
]
