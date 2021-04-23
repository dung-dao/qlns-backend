from django.db import models


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
    date = models.DateField()

    # Actual Working Hours
    actual_work_hours = models.FloatField(default=0)
    actual_hours_modified = models.BooleanField(default=False)
    actual_hours_modification_note = models.TextField(null=True)

    ot_work_hours = models.FloatField(default=0)
    ot_hours_modified = models.BooleanField(default=False)
    ot_hours_modification_note = models.TextField(null=True)

    status = models.CharField(max_length=15, choices=AttendanceLogStatus.choices, default='Pending')

    def calculate_work_hours(self):
        self.actual_work_hours = sum(map(lambda e: e.get_actual_work_hours(), self.tracking_data.all()))

        self.ot_work_hours = sum(map(lambda e: e.get_ot_hours(), self.tracking_data.all()))

        self.save()
