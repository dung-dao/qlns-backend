from django.db import models


class Tracking(models.Model):
    attendance = models.ForeignKey(to='Attendance', on_delete=models.CASCADE, related_name='tracking_data')
    overtime_type = models.ForeignKey(to='OvertimeType', null=True, on_delete=models.SET_NULL)

    check_in_time = models.DateTimeField()
    check_in_lat = models.FloatField(null=True)
    check_in_lng = models.FloatField(null=True)
    check_in_outside = models.BooleanField(null=True)

    check_out_time = models.DateTimeField(null=True)
    check_out_lat = models.FloatField(null=True)
    check_out_lng = models.FloatField(null=True)
    check_out_outside = models.BooleanField(null=True)

    check_in_note = models.TextField(null=True)
    check_out_note = models.TextField(null=True)

    location = models.ForeignKey(to='job.Location', on_delete=models.SET_NULL, null=True)

    def get_ot_hours(self):
        if self.check_in_time is None or self.check_out_time is None:
            return 0

        duration = (self.check_out_time - self.check_in_time).seconds / 3600
        return duration if self.overtime_type is not None else 0

    def get_actual_work_hours(self):
        if self.check_in_time is None or self.check_out_time is None:
            return 0

        duration = (self.check_out_time - self.check_in_time).seconds / 3600
        return duration if self.overtime_type is None else 0
