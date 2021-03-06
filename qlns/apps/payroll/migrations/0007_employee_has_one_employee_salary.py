# Generated by Django 3.1.7 on 2021-05-02 09:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_dependent'),
        ('payroll', '0006_payroll'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employeesalary',
            name='owner',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='salary_info', to='core.employee'),
        ),
    ]
