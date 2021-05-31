# Generated by Django 3.1.7 on 2021-05-01 06:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_dependent'),
        ('payroll', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeSalary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salary', models.DecimalField(decimal_places=2, max_digits=18)),
                ('insurance_policy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payroll.insurancepolicy')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_info', to='core.employee')),
                ('tax_policy', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='payroll.taxpolicy')),
            ],
        ),
    ]