# Generated by Django 3.1.7 on 2021-05-14 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0008_job_event'),
    ]

    operations = [
        migrations.DeleteModel(
            name='JobEvent',
        ),
    ]
