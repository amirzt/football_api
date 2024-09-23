import datetime
import threading

import requests
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from games.models import League, RankingGroup, GroupMember, Team, Match, FootballApiKey, LeagueCheck, DateChecked
from games.serializers import LeagueSerializer, AddBetSerializer, GroupSerializer
from games.utils import calculate_score
from users.models import CustomUser
from users.serializers import CustomUserSerializer
from django.db.models import Q, OuterRef, Exists
import schedule
import time

football_api_url = "https://apiv3.apifootball.com/"


def send_football_api(params):
    try:
        response = requests.get(football_api_url, params=params)
        response.raise_for_status()  # Raise an exception for HTTP errors
        teams_data = response.json()

        return teams_data

    except requests.RequestException as e:
        send_football_api(params)


def get_status(param):
    if param == 'Finished':
        return Match.MatchStatus.finished

    elif param == 'Half Time':
        return Match.MatchStatus.halfTime
    elif param == '':
        return Match.MatchStatus.upcoming
    else:
        return param


def get_matches(league, date):
    params = {
        "action": "get_events",
        "APIkey": FootballApiKey.objects.all().last().token,
        "league_id": league,
        "from": date,
        "to": date
    }

    data = send_football_api(params)
    # print(data)
    message = 'start'

    if 'error' not in data:

        for match in data:
            # print(match)
            game = Match.objects.filter(code=match['match_id'])
            if game.count() > 0:
                game = Match.objects.get(code=match['match_id'])
                game.home_score = int(0) if (match['match_hometeam_score']) == "" else int(
                    match['match_hometeam_score'])
                game.away_score = int(0) if (match['match_awayteam_score']) == "" else int(
                    match['match_awayteam_score'])
                game.status = get_status(match['match_status'])
                game.stadium = match['match_stadium']
                game.referee = match['match_referee']
                game.league_round = match['match_round']
                game.save()
                message = 'Success'

            else:
                game, created = Match.objects.update_or_create(
                    code=match['match_id'],
                    league=League.objects.get(code=league),
                    home=Team.objects.get(code=match['match_hometeam_id']),
                    away=Team.objects.get(code=match['match_awayteam_id']),
                    home_score=0 if match['match_hometeam_score'] == "" else match['match_hometeam_score'],
                    away_score=0 if match['match_awayteam_score'] == "" else match['match_awayteam_score'],
                    date=match['match_date'],
                    time=match['match_time'],
                    stadium=match['match_stadium'],
                    referee=match['match_referee'],
                    league_round=match['match_round'],
                    status=get_status(match['match_status']),

                )
                if created:
                    message = 'Success'
                else:
                    message = 'Fail'

    elif data['error'] == 404:
        league_check = LeagueCheck(league=League.objects.get(code=league),
                                   date_field=date)
        league_check.save()

    return Response(data={"message": message})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_league(request):
    # checks_for_date = LeagueCheck.objects.filter(
    #     league=OuterRef('pk'),
    #     date_field=request.data['date']
    # ).values('id')

    user_date = datetime.datetime.strptime(request.data['date'], "%Y-%m-%d").date()
    today = datetime.date.today()

    if user_date != today:
        check_date = DateChecked.objects.filter(date=user_date)
        if check_date.count() == 0:
            checks_for_date = LeagueCheck.objects.filter(
                league=OuterRef('pk'),
                date_field=request.data['date']
            ).values('id')
            # leagues = League.objects.filter(active=True)
            leagues = League.objects.filter(~Exists(checks_for_date),
                                            active=True)

            # get_matches(18, request.data['date'], request.user.id)

            for league in leagues:
                get_matches(league.code, user_date)
            cd = DateChecked(date=user_date)
            cd.save()

    leagues = League.objects.filter(active=True)

    # get_matches(18, request.data['date'], request.user.id)

    # for league in leagues:
    #     get_matches(league.code, request.data['date'])

    leagues = leagues.filter(Q(match__date=request.data['date'])).distinct()
    serializer = LeagueSerializer(leagues, many=True,
                                  context={"user": CustomUser.objects.get(id=request.user.id),
                                           "date": request.data['date']})

    # calculate score
    data = {
        'user': request.user.id,
        'date': user_date
    }
    thread = threading.Thread(target=calculate_score,
                              args=[data])
    thread.setDaemon(True)
    thread.start()
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

    user_index = next((index for index, user in enumerate(users) if user.id == request.user.id), None)

    serializer = CustomUserSerializer(users, many=True)
    return Response({
        "data": serializer.data,
        "your_ranking": user_index + 1
    })


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

    if user.expire_date < timezone.now():
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "Your subscription has expired."})
    else:
        group = RankingGroup(name=request.data['name'],
                             username=request.data['username'],
                             creator=user)
        group.save()
        member = GroupMember(user=user, group=group)
        member.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_group(request):
    user = CustomUser.objects.get(id=request.user.id)
    try:
        group = RankingGroup.objects.get(username=request.data['username'])

        member = GroupMember(user=user, group=group)
        member.save()
        return Response(status=status.HTTP_200_OK)
    except RankingGroup.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_group(request):
    user = CustomUser.objects.get(id=request.user.id)
    try:
        group = RankingGroup.objects.get(id=request.data['id'])

        member = GroupMember.objects.get(user=user, group=group)
        member.delete()
        return Response(status=status.HTTP_200_OK)
    except RankingGroup.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)


def get_teams_data(params):
    teams_data = send_football_api(params)
    for team_data in teams_data:
        #
        # # Save the image to a temporary file
        # img_temp = NamedTemporaryFile(delete=True)
        # img_temp.write(response.content)
        # img_temp.flush()

        team, created = Team.objects.update_or_create(
            code=team_data['team_key'],
            name=team_data['team_name'],
            logo=team_data['team_badge']
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def add_team(request):
    params = {
        "action": "get_teams",
        "APIkey": FootballApiKey.objects.all().last().token,
        "league_id": request.data['league']
    }

    thread = threading.Thread(target=get_teams_data,
                              args=[params])
    thread.setDaemon(True)
    thread.start()
    # teams_data = send_football_api(params)
    # for team_data in teams_data:
    #     #
    #     # # Save the image to a temporary file
    #     # img_temp = NamedTemporaryFile(delete=True)
    #     # img_temp.write(response.content)
    #     # img_temp.flush()
    #
    #     team, created = Team.objects.update_or_create(
    #         code=team_data['team_key'],
    #         name=team_data['team_name'],
    #         logo=team_data['team_badge']
    #     )

    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_match(request):
    league = League.objects.get(code=request.data['league'])

    params = {
        "action": "get_events",
        "APIkey": FootballApiKey.objects.all().last().token,
        "league_id": request.data['league'],
        "from": '2024-09-01',
        "to": '2024-09-01'
    }

    data = send_football_api(params)
    # print(data)
    message = 'start'
    for match in data:
        print(match)
        game, created = Match.objects.update_or_create(
            league=league,
            home=Team.objects.get(code=match['match_hometeam_id']),
            away=Team.objects.get(code=match['match_awayteam_id']),
            date=match['match_date'],
            time=match['match_time'],
        )
        if created:
            message = 'Success'
        else:
            message = 'Fail'
    return Response(data={"message": message})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export(request):
    data = {}
    leagues = League.objects.all()
    teams = Team.objects.all()

    for league in leagues:
        data[league.name] = league.name

    for team in teams:
        data[team.name] = team.name

    return Response(data=data)


def job():
    print('started')
    date = datetime.date.today()
    # print(date)
    # leagues = League.objects.filter(active=True)
    checks_for_date = LeagueCheck.objects.filter(
        league=OuterRef('pk'),
        date_field=date
    ).values('id')
    leagues = League.objects.filter(~Exists(checks_for_date),
                                    active=True)

    # get_matches(18, request.data['date'], request.user.id)

    for league in leagues:
        get_matches(league.code, date)
    print('finished')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def run_schedule(request):
    schedule.every(1).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(0)
