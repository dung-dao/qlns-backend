# Generated by Django 3.1.7 on 2021-04-09 14:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_employeelicense'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeLanguage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.CharField(choices=[('Reading', 'Reading'), ('Speaking', 'Speaking'), ('Writing', 'Writing')], max_length=20)),
                ('fluency_level', models.CharField(choices=[('Poor', 'Poor'), ('Basic', 'Basic'), ('Good', 'Good'), ('Mother Tongue', 'Mothertongue')], max_length=20)),
                ('note', models.TextField(blank=True)),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.language')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='languages', to='core.employee')),
            ],
        ),
    ]