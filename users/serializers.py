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
    class Meta:
        model = CustomUser
        fields = ['email', 'expire_date', 'name']


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
