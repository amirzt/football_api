from datetime import datetime

from django.utils import timezone
from rest_framework import serializers

from users.models import CustomUser, Admob, CustomAd, Lottery


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['password', 'email']
        extra_kwargs = {"password": {"write_only": True}}

    def save(self, **kwargs):
        user = CustomUser(email=self.validated_data['email'])
        user.set_password(self.validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(serializers.ModelSerializer):
    expired = serializers.SerializerMethodField('get_expired')

    def get_expired(self, obj):
        return obj.expire_date < timezone.now()

    class Meta:
        model = CustomUser
        fields = ['email', 'expire_date', 'name', 'score', 'image', 'expired']


class AdmobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admob
        fields = '__all__'


class CustomAdSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomAd
        fields = '__all__'


class LotterySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lottery
        fields = '__all__'
