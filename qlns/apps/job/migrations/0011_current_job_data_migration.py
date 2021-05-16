from django.db import migrations


def combine_names(apps, schema_editor):
    Employee = apps.get_model('core', 'Employee')
    for employee in Employee.objects.all():
        job = employee.job_history.order_by('-timestamp').first()
        employee.current_job = job
        employee.save()


class Migration(migrations.Migration):
    dependencies = [
        ('job', '0010_termination_models'),
    ]

    operations = [
        migrations.RunPython(combine_names)
    ]
