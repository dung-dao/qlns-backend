# Generated by Django 3.1.7 on 2021-04-02 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_contactinfo'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmergencyContact',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=150)),
                ('relationship', models.CharField(max_length=50)),
                ('phone', models.CharField(max_length=20)),
                ('owner', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='emergency_contact', to='core.employee')),
            ],
        ),
    ]
