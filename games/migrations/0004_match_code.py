# Generated by Django 5.0.7 on 2024-09-01 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0003_rankinggroup_groupmember'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='code',
            field=models.CharField(blank=True, default=None, max_length=100, null=True),
        ),
    ]
