from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.models import League
from games.serializers import LeagueSerializer, AddBetSerializer
from users.models import CustomUser
from users.serializers import CustomUserSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_league(request):
    leagues = League.objects.all()
    serializer = LeagueSerializer(leagues, many=True,
                                  context={"user": CustomUser.objects.get(id=request.user.id),
                                           "date": request.data['date']})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bet(request):
    serializer = AddBetSerializer(data=request.data,
                                  context={"user": CustomUser.objects.get(id=request.user.id), })
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_ranking(request):
    users = CustomUser.objects.all().order_by('-score')
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)
