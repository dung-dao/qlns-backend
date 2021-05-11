from django.db import models

from qlns.apps.attendance import models as attendance_models


class Attendance(models.Model):
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

    def calculate_work_hours(self):
        trackers = attendance_models.Tracking.objects.filter(attendance=self.pk)
        for t in trackers:
            t.actual_work_hours = t.get_actual_work_hours()
            t.ot_work_hours = t.get_ot_hours()
            t.save()
        self.actual_work_hours = sum(map(lambda e: e.actual_work_hours, trackers))

        self.ot_work_hours = sum(map(lambda e: e.ot_work_hours, trackers))

        self.save()
