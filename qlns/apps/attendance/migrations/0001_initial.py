# Generated by Django 3.1.7 on 2021-04-17 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='WorkDay',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu', 'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')], max_length=3)),
                ('morning_from', models.TimeField(blank=True, null=True)),
                ('morning_to', models.TimeField(blank=True, null=True)),
                ('afternoon_from', models.TimeField(blank=True, null=True)),
                ('afternoon_to', models.TimeField(blank=True, null=True)),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workdays', to='attendance.schedule')),
            ],
        ),
    ]