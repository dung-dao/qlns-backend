# Generated by Django 3.1.7 on 2021-05-08 04:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0023_restore_confirmed_status'),
    ]

    operations = [
        migrations.RunSQL("DELETE FROM qlns.attendance_tracking"),
        migrations.RunSQL("DELETE FROM qlns.attendance_attendance")
    ]
