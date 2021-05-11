# Generated by Django 3.1.7 on 2021-05-01 09:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payroll', '0003_payrollconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('is_default', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SalaryTemplateField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('index', models.IntegerField()),
                ('type', models.CharField(choices=[('System Field', 'Systemfield'), ('Formula', 'Formula')], max_length=50)),
                ('code_name', models.CharField(max_length=255)),
                ('display_name', models.CharField(max_length=255)),
                ('define', models.CharField(blank=True, max_length=1024, null=True)),
                ('templates', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='payroll.salarytemplate')),
            ],
        ),
    ]
