# Generated by Django 3.1.7 on 2021-06-19 15:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0028_employee_recognition_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='face_model_path',
        ),
    ]
