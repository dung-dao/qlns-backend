# Generated by Django 3.1.7 on 2021-04-26 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0010_timeoff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='workday',
            name='afternoon_from',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workday',
            name='afternoon_to',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workday',
            name='morning_from',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='workday',
            name='morning_to',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
