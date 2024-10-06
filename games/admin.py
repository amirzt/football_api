from django.contrib import admin

# Register your models here.
from games.models import League, Team, Match, Bet, RankingGroup, FootballApiKey, APILog, DateChecked


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'created_at', 'updated_at')
    search_fields = ('name__startswith',)
    fields = ('name', 'logo', 'code', 'active', 'description',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name__startswith',)
    fields = ('name', 'logo', 'code', 'description',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'league', 'code', 'home', 'away', 'date', 'time', 'home_score', 'away_score', 'status', 'description',
        'created_at',
        'updated_at')
    fields = (
        'league', 'home', 'away', 'date', 'time', 'home_score', 'away_score', 'status', 'description', 'stadium',
        'referee', 'league_round')


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('match', 'user', 'created_at', 'updated_at')
    search_fields = ('name__startswith',)
    fields = ('match', 'user', 'home_score', 'away_score', 'score')


@admin.register(RankingGroup)
class BetAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'description', 'creator', 'created_at', 'updated_at')
    search_fields = ('name__startswith',)
    fields = ('name', 'username', 'description', 'creator',)


admin.site.register(FootballApiKey)
# admin.site.register(LeagueCheck)
admin.site.register(APILog)
admin.site.register(DateChecked)