# Generated by Django 3.1.7 on 2021-06-19 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_applicationconfig_allow_unrecognised_face'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='recognition_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]