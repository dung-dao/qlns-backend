# Generated by Django 3.1.7 on 2021-06-01 09:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_seed_application_config'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='employee',
            options={'default_permissions': ('add', 'change', 'view'), 'permissions': (('can_set_role_employee', 'Can change employee role'), ('can_set_password_employee', 'Can change employee password'), ('can_change_avatar_employee', 'Can change employee avatar (also use for face identity)'))},
        ),
    ]
