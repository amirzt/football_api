from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import CustomUser, Admob, CustomAd, Lottery
from users.serializers import RegistrationSerializer, CustomUserSerializer, AdmobSerializer, CustomAdSerializer, \
    LotterySerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    try:
        user = CustomUser.objects.get(email=request.data['email'])

        if user.check_password(request.POST.get('password')):
            user.is_active = True
            user.save()

            token, created = Token.objects.get_or_create(user=user)

            # otp = OTP(user=user)
            # otp.save()
            # send_otp(otp.code, user.phone)

            return Response({
                'token': token.key,
                'exist': True
            }, status=200)
        else:
            return Response({
                'message': 'رمز ورود اشتباه است'
            }, status=403)

    except CustomUser.DoesNotExist:
        user_serializer = RegistrationSerializer(data=request.data)

        if user_serializer.is_valid():
            user = user_serializer.save()

            user.is_active = True
            user.save()

            # otp = OTP(user=user)
            # otp.save()
            # send_otp(otp.code, user.phone)

            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'exist': False
            })

        else:
            return Response(user_serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([AllowAny])
def splash(request):
    admob = Admob.objects.filter(active=True)
    customs = CustomAd.objects.filter(active=True)
    lottery = Lottery.objects.filter(active=True)

    return Response(status=status.HTTP_200_OK,
                    data={
                        "admob": AdmobSerializer(admob, many=True).data,
                        "customs": CustomAdSerializer(customs, many=True).data,
                        "lottery": LotterySerializer(lottery, many=True).data
                    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_user(request):
    user = CustomUser.objects.get(id=request.user.id)
    return Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update(request):
    user = CustomUser.objects.get(id=request.user.id)
    if 'name' in request.data:
        users = CustomUser.objects.filter(name=request.data['name'])
        if users.count() > 0:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        user.name = request.data['name']
    if 'image' in request.data:
        user.image = request.data['image']
    user.save()
    return Response(CustomUserSerializer(user).data, status=status.HTTP_200_OK)
