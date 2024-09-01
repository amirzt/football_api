from django.db import models

from users.models import CustomUser


class League(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    logo = models.ImageField(upload_to='league/logo/', null=False, blank=False)
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    active = models.BooleanField(default=True)
    description = models.TextField(max_length=1000, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    logo = models.CharField(max_length=1000, null=True, blank=True, default=None)
    code = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.TextField(max_length=1000, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    class MatchStatus(models.TextChoices):
        upcoming = 'upcoming'
        playing = 'playing'
        finished = 'finished'
        canceled = 'canceled'

    league = models.ForeignKey(League, on_delete=models.CASCADE)
    home = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home')
    away = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away')
    date = models.DateField()
    time = models.TimeField(default='00:00')
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    status = models.CharField(max_length=100, choices=MatchStatus.choices, default=MatchStatus.upcoming)
    description = models.TextField(max_length=1000, null=True, blank=True)
    code = models.CharField(max_length=100, null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.league.name


class FavouriteLeague(models.Model):
    league = models.ForeignKey(League, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('league', 'user')


class Bet(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    score = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('match', 'user')


class RankingGroup(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    username = models.CharField(max_length=100, null=False, blank=False, unique=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GroupMember(models.Model):
    group = models.ForeignKey(RankingGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('group', 'user')


class FootballApiKey(models.Model):
    token = models.CharField(max_length=500, null=False, blank=False)