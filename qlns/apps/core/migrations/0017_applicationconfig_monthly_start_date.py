# Generated by Django 3.1.7 on 2021-05-08 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_applicationconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationconfig',
            name='monthly_start_date',
            field=models.IntegerField(default=1),
        ),
    ]
