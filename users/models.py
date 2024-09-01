from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models

# Create your models here.
from users.managers import CustomUserManager


def get_yesterday_date():
    from datetime import date, timedelta
    return date.today() + timedelta(days=30)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class AppType(models.TextChoices):
        bazar = 'bazar'
        myket = 'myket'
        googleplay = 'googleplay'
        web = 'web'
        ios = 'ios'

    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    name = models.CharField(max_length=100, null=True, blank=True)
    score = models.IntegerField(default=0)
    credit = models.IntegerField(default=0)
    image = models.ImageField(upload_to='user/image/', default=None, null=True)

    is_visible = models.BooleanField(default=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    date_joint = models.DateField(auto_now_add=True)
    expire_date = models.DateTimeField(null=True, blank=True, default=get_yesterday_date)

    app_type = models.CharField(default=AppType.bazar, choices=AppType.choices, max_length=20)
    version = models.CharField(default='0.0.0', max_length=20)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class TypeChoices(models.TextChoices):
    BANNER = 'banner'
    INTERSTITIAL = 'interstitial'
    REWARDED = 'rewarded'


class Admob(models.Model):
    type = models.CharField(choices=TypeChoices.choices, max_length=20)
    code = models.CharField(max_length=1000)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class CustomAd(models.Model):
    banner = models.ImageField(upload_to='ad/custom/', null=False)
    name = models.CharField(max_length=100, null=False)
    link = models.URLField(max_length=1000, null=False, blank=False)
    active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Lottery(models.Model):
    fa_title = models.CharField(max_length=100)
    fa_description = models.TextField(max_length=1000)
    en_title = models.CharField(max_length=100)
    en_description = models.TextField(max_length=1000)
    active = models.BooleanField(default=True)
    price = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
