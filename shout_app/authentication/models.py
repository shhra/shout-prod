from allauth.account.models import EmailAddress
from django.contrib.auth.models import (
        AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from datetime import datetime, timedelta
from django.conf import settings
from django.db import models


class UserManager(BaseUserManager):
    """
    This is a custom user manager to manage the shouters.
    """
    def create_user(self, username, password):
        if not username:
            raise ValueError("Enter valid username")
        if not password:
            raise ValueError("Please Enter Password")
        user = self.model(
             username = username,
             )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password):
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    A custom user class for managing user data
    TODO
    1. Add phone field
    """
    first_name = models.CharField(max_length=1, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=1, blank=True, null=True, default=None)
    username = models.CharField(max_length=128, unique=True)
    location = models.CharField(max_length=10, blank=True)
    email = models.EmailField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    # with is_active off, we can create deactivation feature.
    is_active = models.BooleanField(default=True) 
    is_staff = models.BooleanField(default=False)
    is_professional = models.BooleanField(default=False)
    # user joined date
    created_at = models.DateTimeField(auto_now_add=True)
    objects = UserManager()
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = []

    def __str__(self):
        return "{}".format(self.username)

    def account_verified(self):
        if self.is_authenticated:
            result = EmailAddress.objects.filter(email=self.email)
            if len(result):
                return result[0].verified
        return False
