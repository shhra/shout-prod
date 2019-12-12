import itertools
import uuid
from requests import get
"""
Core Tables
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from allauth.account.models import EmailAddress


url = 'http://127.0.0.1:5000/encode'

class SoftDeletionManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(SoftDeletionManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return SoftDeletionQuerySet(self.model).filter(deleted_at=None)
        return SoftDeletionQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()


class SoftDeletionQuerySet(models.QuerySet):
    def delete(self):
        return super(SoftDeletionQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        return super(SoftDeletionQuerySet, self).delete()

    def alive(self):
        return self.filter(deleted_at=None)

    def dead(self):
        return self.exclude(deleted_at=None)


class SoftDeletionModel(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True)

    objects = SoftDeletionManager()
    all_objects = SoftDeletionManager(alive_only=False)

    class Meta:
        abstract = True

    def delete(self):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self):
        super(SoftDeletionModel, self).delete()


class DateTimeModel(SoftDeletionModel):
    """
    This model will be abstract model for handling every timestamp in it's chlid object.
    """
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    class Meta:
        abstract = True


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


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    A custom user class for managing user data
    TODO
    1. Add phone field
    """
    first_name = models.CharField(max_length=1, blank=True, null=True, default=None)
    last_name = models.CharField(max_length=1, blank=True, null=True, default=None)
    username = models.CharField(max_length=25, unique=True)
    location = models.CharField(max_length=10, blank=True)
    email = models.EmailField(max_length=255)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_professional = models.BooleanField(default=False)

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


class Shout(DateTimeModel):
    """
    Represent the shouts made by the user
    """
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=80, unique=True, default=uuid.uuid4, null=True)
    body = models.CharField(max_length=9999)
    sentiment = models.CharField(max_length=8, default='NEUTRAL')
    value = models.BinaryField(max_length=4000, null=True, blank=True, default=None)
    shouter = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
            related_name='shout_user')
    date = models.DateTimeField(auto_now_add=True)
    supporters = models.ManyToManyField(CustomUser, related_name='shout_supporters')
    threshold = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        max_length = Shout._meta.get_field('title').max_length
        self.slug = orig = slugify(self.title)[:max_length]

        for x in itertools.count(1):
            if self.id:
                if Shout.all_objects.filter(
                                  models.Q(slug=self.slug),
                                  models.Q(shouter=self.shouter),
                                  models.Q(id=self.id),
                                 ).exists():
                    break
            if not Shout.all_objects.filter(slug=self.slug).exists():
                break
            # Truncate & Minus 1 for the hyphen.
            self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
        encoded_value = get(f'{url}?shout={self.body}')
        print(f'{url}?shout={self.body}')
        print(encoded_value)
        self.value = encoded_value.content
        super(Shout, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("master:shout_detail", kwargs={"slug": self.slug})


class Comment(DateTimeModel):
    """
    A global class for commenting
    """
    text = models.CharField(max_length=9999)
    slug = models.SlugField(max_length=80, unique=True, default=uuid.uuid4, null=True)
    commented_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    commented_on = models.ForeignKey(Shout, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        max_length = Comment._meta.get_field('text').max_length
        self.slug = orig = slugify(self.text)[:max_length]

        for x in itertools.count(1):
            if self.id:
                if Comment.all_objects.filter(
                                  models.Q(slug=self.slug),
                                  models.Q(commented_by=self.commented_by),
                                  models.Q(id=self.id),
                                 ).exists():
                    break
            if not Comment.all_objects.filter(slug=self.slug).exists():
                break
            # Truncate & Minus 1 for the hyphen.
            self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
        super(Comment, self).save(*args, **kwargs)


class Discussion(DateTimeModel):
    """
    A discussion hub that is opened to users who follow a shout.
    """
    shout = models.OneToOneField(Shout, on_delete=models.CASCADE)
    comments = models.ForeignKey(Comment, on_delete=models.CASCADE)
    banned = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
