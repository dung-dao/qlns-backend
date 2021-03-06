# Generated by Django 3.1.7 on 2021-06-01 06:44

from django.db import migrations


def forward(apps, schema_editor):
    ApplicationConfig = apps.get_model("core", "ApplicationConfig")
    config = ApplicationConfig.objects.first()
    if config is None:
        config = ApplicationConfig(
            early_check_in_minutes=30,
            monthly_start_date=1,
            ot_point_rate=1.5,
            require_face_id=False
        )
        config.save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0024_employee_face_model'),
    ]

    operations = [
        migrations.RunPython(forward)
    ]
