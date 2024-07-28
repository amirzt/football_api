from rest_framework import serializers

from games.models import League, Team, Bet, Match, FavouriteLeague


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'


class BetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    home = TeamSerializer()
    away = TeamSerializer()
    bet = serializers.SerializerMethodField('get_bet')

    def get_bet(self, data):
        try:
            bet = Bet.objects.get(match=data,
                                  user=self.context.get('user'))
            return BetSerializer(bet).data
        except Bet.DoesNotExist:
            return {}

    class Meta:
        model = Match
        fields = '__all__'


class LeagueSerializer(serializers.ModelSerializer):
    matches = serializers.SerializerMethodField('get_matches')
    is_fav = serializers.SerializerMethodField('get_is_fav')

    def get_matches(self, data):
        matches = Match.objects.filter(date=self.context.get('date'),
                                       league=data)
        return MatchSerializer(matches, many=True).data

    def get_is_fav(self, data):
        fav = FavouriteLeague.objects.filter(user=self.context.get('user'),
                                             league=data)
        return False if fav.count() == 0 else True

    class Meta:
        model = League
        fields = '__all__'


class AddBetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bet
        fields = ['match', 'home_score', 'away_score']

    def save(self, **kwargs):
        bet = Bet(match=self.validated_data['match'],
                  home_score=self.validated_data['home_score'],
                  away_score=self.validated_data['away_score'],
                  user=self.context.get('user'))
        bet.save()
        return bet
