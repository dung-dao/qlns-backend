# Generated by Django 3.1.7 on 2021-05-24 08:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_employee_current_job'),
        ('payroll', '0019_migrate_existing_system_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='payroll',
            name='confirmed_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.employee'),
        ),
    ]
