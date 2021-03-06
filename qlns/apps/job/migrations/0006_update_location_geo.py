# Generated by Django 3.1.7 on 2021-04-21 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0005_modify_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='enable_geofencing',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='location',
            name='accurate_address',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='allow_outside',
            field=models.BooleanField(null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='radius',
            field=models.FloatField(null=True),
        ),
    ]
