# Generated by Django 3.1.7 on 2021-04-18 12:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_employeeskill'),
        ('attendance', '0002_employeeschedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('actual_work_hours', models.FloatField(default=0)),
                ('ot_work_hours', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected'), ('Confirmed', 'Confirmed')], max_length=15)),
                ('confirmed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='confirmed_attendance', to='core.employee')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.employee')),
                ('reviewed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='reviewed_attendance', to='core.employee')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='attendance.schedule')),
            ],
        ),
        migrations.CreateModel(
            name='OvertimeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('point_rate', models.FloatField()),
            ],
        ),
        migrations.AlterField(
            model_name='employeeschedule',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employee_schedule', to='core.employee'),
        ),
        migrations.CreateModel(
            name='Tracking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('check_in_time', models.DateTimeField()),
                ('check_in_lat', models.FloatField(null=True)),
                ('check_in_lng', models.FloatField(null=True)),
                ('check_in_outside', models.BooleanField(null=True)),
                ('check_out_time', models.DateTimeField(null=True)),
                ('check_out_lat', models.FloatField(null=True)),
                ('check_out_lng', models.FloatField(null=True)),
                ('check_out_outside', models.BooleanField(null=True)),
                ('is_ot', models.BooleanField(default=False)),
                ('check_in_note', models.TextField()),
                ('check_out_note', models.TextField()),
                ('attendance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracking_data', to='attendance.attendance')),
                ('overtime_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='attendance.overtimetype')),
            ],
        ),
    ]
