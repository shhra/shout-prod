import itertools
import uuid
import re
from requests import get
from random import randint
from django.contrib.postgres.fields import ArrayField
import os

"""
Core Tables
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from allauth.account.models import EmailAddress
from shout_app.core.models import DateTimeModel


url = os.getenv('ENC_URL') + '/encode'



class Shout(DateTimeModel):
    """
    Represent the shouts made by the user
    """
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=80, unique=True, default=uuid.uuid4, null=True)
    body = models.CharField(max_length=420)
    sentiment = models.CharField(max_length=8, default='NEUTRAL')
    value = ArrayField(
            ArrayField(
                models.FloatField(max_length=16, blank=True, null=True),
                size=768,
                null=True
                ),
            size=420,
            null=True
            )
    shouter = models.ForeignKey('profile.Profile', on_delete=models.CASCADE,
            related_name='shouts')
    threshold = models.PositiveIntegerField(default=5)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        max_length = Shout._meta.get_field('title').max_length
        value = self.title
        if not re.search("^[a-zA-Z0-9]", self.title) :
            value = value + str(chr(randint(65, 90))) + str(chr(randint(97, 122)))
        self.slug = orig = slugify(value)[:max_length]

        for x in itertools.count(1):
            if not Shout.all_objects.filter(slug=self.slug).exists():
                break
            # Truncate & Minus 1 for the hyphen.
            self.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)
        encoded_value = get(url=url, json={"shout": self.body})
        self.value = encoded_value.json()['encodings']
        super(Shout, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("master:shout_detail", kwargs={"slug": self.slug})


class Comment(DateTimeModel):
    """
    A global class for commenting
    """
    text = models.CharField(max_length=499)
    slug = models.SlugField(max_length=80, unique=True, default=uuid.uuid4, null=True)
    commented_by = models.ForeignKey('profile.Profile', on_delete=models.CASCADE)
    commented_on = models.ForeignKey(Shout, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        max_length = Comment._meta.get_field('text').max_length
        self.slug = orig = slugify(self.text)[:max_length]

        for x in itertools.count(1):
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
    comments = models.ManyToManyField('shouts.Comment', related_name='discussion_comment')
    banned = models.ManyToManyField('profile.Profile', related_name='banned_user')

    def ban_user(self, profile):
        return self.banned.add(profile)

    def unban_user(self, profile):
        return self.banned.remove(profile)

    def is_banned(self, profile):
        return self.banned.filter(pk=profile.pk).exists
