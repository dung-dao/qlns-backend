# Generated by Django 3.1.7 on 2021-04-26 07:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_employeeskill'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dependent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateTimeField(blank=True, null=True)),
                ('gender', models.CharField(blank=True, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], max_length=50, null=True)),
                ('relationship', models.CharField(blank=True, max_length=255, null=True)),
                ('province', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('personal_id', models.CharField(max_length=20, null=True, blank=True)),
                ('personal_tax_id', models.CharField(max_length=30, null=True, blank=True)),
                ('effective_start_date', models.DateTimeField(null=True)),
                ('effective_end_date', models.DateTimeField(null=True)),
                ('nationality', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.country')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Dependents', to='core.employee')),
            ],
        ),
    ]
