# Generated by Django 5.0.7 on 2024-09-12 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_alter_lotterychance_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='zarinpal_url',
            field=models.URLField(default=None, max_length=1000, null=True),
        ),
    ]