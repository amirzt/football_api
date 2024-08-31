import datetime

from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.models import League, RankingGroup, GroupMember
from games.serializers import LeagueSerializer, AddBetSerializer, GroupSerializer
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from django.db.models import Q


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_league(request):
    leagues = League.objects.filter(Q(match__date=request.data['date'])).distinct()
    leagues.filter(active=True)
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
    if 'group' in request.data:
        group = RankingGroup.objects.get(id=request.data['group'])
        users = CustomUser.objects.filter(groupmember__group=group).order_by('-score')
    else:
        users = CustomUser.objects.all().order_by('-score')
    serializer = CustomUserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_groups(request):
    user = CustomUser.objects.get(id=request.user.id)
    groups = RankingGroup.objects.filter(groupmember__user=user)
    serializer = GroupSerializer(groups, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_group(request):
    user = CustomUser.objects.get(id=request.user.id)

    group = RankingGroup(name=request.data['name'],
                         username=request.data['username'],
                         creator=user)
    group.save()
    member = GroupMember(user=user, group=group)
    member.save()
    return Response(status=status.HTTP_200_OK)

    # if user.expire_date < datetime.datetime.now():
    #     return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Your subscription has expired."})
    # else:
    #     group = RankingGroup(name=request.data['name'],
    #                          username=request.data['username'],
    #                          creator=user)
    #     group.save()
    #     member = GroupMember(user=user, group=group)
    #     member.save()
    #     return Response(status=status.HTTP_200_OK)
