# Generated by Django 5.0.7 on 2024-09-01 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0007_match_league_round_match_referee_match_stadium'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='status',
            field=models.CharField(default='upcoming', max_length=100),
        ),
    ]
