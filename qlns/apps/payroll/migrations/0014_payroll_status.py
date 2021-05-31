# Generated by Django 3.1.7 on 2021-05-17 02:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0013_auto_20210509_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='status',
            field=models.CharField(choices=[('Temporary', 'Temporary'), ('Confirmed', 'Confirmed')], default='Temporary', max_length=50),
        ),
    ]