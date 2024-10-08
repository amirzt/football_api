# Generated by Django 5.0.7 on 2024-09-15 07:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0010_bet_is_calculated'),
    ]

    operations = [
        migrations.CreateModel(
            name='LeagueCheck',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='games.league')),
            ],
        ),
    ]
