from django.db import models
from django.db.models import Q

from qlns.apps.attendance import models as attendance_models


class Attendance(models.Model):
    class Meta:
        default_permissions = ('view',)
        permissions = (
            ('can_revert_attendance', 'Can revert employee attendance'),
            ('can_reject_attendance', 'Can reject employee attendance'),
            ('can_approve_attendance', 'Can approve employee attendance'),
            ('can_confirm_attendance', 'Can confirm employee attendance'),
            ('can_edit_actual_hours_attendance', 'Can edit actual hours of an employee attendance'),
            ('can_edit_overtime_hours_attendance', 'Can edit overtime hours of an employee attendance'),
        )

    class AttendanceLogStatus(models.TextChoices):
        Pending = 'Pending'
        Approved = 'Approved'
        Rejected = 'Rejected'
        Confirmed = 'Confirmed'

    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE, related_name='attendance')
    reviewed_by = models.ForeignKey(to='core.Employee', on_delete=models.PROTECT,
                                    null=True, related_name='reviewed_attendance')
    confirmed_by = models.ForeignKey(to='core.Employee', on_delete=models.PROTECT,
                                     null=True, related_name='confirmed_attendance')

    schedule = models.ForeignKey(to='Schedule', on_delete=models.PROTECT)
    period = models.ForeignKey(to='Period', on_delete=models.PROTECT, related_name='attendance')
    date = models.DateTimeField()

    # Actual Working Hours
    actual_work_hours = models.FloatField(default=0)
    actual_hours_modified = models.BooleanField(default=False)
    actual_hours_modification_note = models.TextField(null=True)

    ot_work_hours = models.FloatField(default=0)
    ot_hours_modified = models.BooleanField(default=False)
    ot_hours_modification_note = models.TextField(null=True)

    status = models.CharField(max_length=15, choices=AttendanceLogStatus.choices, default='Pending')

    def get_schedule_hours(self):
        period_start_date = self.period.start_date
        period_end_date = self.period.end_date
        schedule_hours = self.schedule.get_schedule_work_hours()

        holidays = attendance_models.Holiday.objects\
            .filter(Q(start_date__gte=period_start_date) & Q(start_date__lte=period_end_date))

        holiday_hours = sum(list(map(lambda hld: hld.trim_work_hours(period_start_date, period_end_date), holidays)))
        return schedule_hours - holiday_hours

    def calculate_work_hours(self):
        trackers = attendance_models.Tracking.objects.filter(attendance=self.pk)
        for t in trackers:
            t.calc_work_hours()
            t.save()

        self.actual_work_hours = sum(map(lambda e: e.actual_work_hours, trackers))
        self.ot_work_hours = sum(map(lambda e: e.ot_work_hours, trackers))
        self.save()
