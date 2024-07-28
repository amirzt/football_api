from django.contrib import admin

# Register your models here.
from games.models import League, Team, Match, Bet


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
        'league', 'home', 'away', 'date', 'home_score', 'away_score', 'status', 'description', 'created_at',
        'updated_at')
    fields = (
        'league', 'home', 'away', 'date', 'home_score', 'away_score', 'status', 'description', 'created_at',
        'updated_at')


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('match', 'user', 'created_at', 'updated_at')
    search_fields = ('name__startswith',)
    fields = ('match', 'user', 'home_score', 'away_score', 'score')
