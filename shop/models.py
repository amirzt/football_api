from django.db import models

# Create your models here.
from users.models import CustomUser


class ZarinpalCode(models.Model):
    code = models.CharField(max_length=255, null=False, blank=False)
    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code


class Plan(models.Model):
    title = models.CharField(max_length=255, null=False, blank=False)
    description = models.TextField(max_length=1000, null=True, blank=True)
    price = models.IntegerField(null=False, blank=False)
    is_available = models.BooleanField(default=True)
    duration = models.IntegerField(null=False, blank=False)
    bazar_myket = models.CharField(max_length=100, default='', null=False)
    zarinpal_url = models.URLField(max_length=1000, null=True, default=None)
    is_special = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Transaction(models.Model):
    class GatewayChoices(models.TextChoices):
        ZARINPAL = 'zarinpal'
        GOOGLEPLAY = 'googleplay'
        APPSTORE = 'appstore'
        BAZAR = 'bazar'
        MYKET = 'myket'

    class StateChoices(models.TextChoices):
        PENDING = 'pending'
        SUCCESS = 'success'
        FAILED = 'failed'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    description = models.TextField(max_length=1000, null=True)
    price = models.FloatField(null=False, blank=False)
    gateway = models.CharField(max_length=255, choices=GatewayChoices.choices)
    gateway_code = models.CharField(max_length=255, null=True)
    tracking_code = models.CharField(max_length=255, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, choices=StateChoices.choices, default=StateChoices.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email + ' - ' + self.plan.title


class LotteryChance(models.Model):
    class StateChoices(models.TextChoices):
        PENDING = 'pending'
        SUCCESS = 'success'
        FAILED = 'failed'
        FINISHED = 'finished'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    state = models.CharField(max_length=255, choices=StateChoices.choices, default=StateChoices.PENDING)
    date = models.DateField(auto_now_add=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, default=None, null=True)
    result = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
