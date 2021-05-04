from django.db import models


class Tracking(models.Model):
    attendance = models.ForeignKey(to='Attendance', on_delete=models.CASCADE, related_name='tracking_data')
    is_overtime = models.BooleanField(default=False)

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
        return duration if self.is_overtime else 0

    def get_actual_work_hours(self):
        if self.check_out_time is None:
            return 0

        schedule = self.attendance.schedule
        return schedule.get_work_hours(self.check_in_time, self.check_out_time)

    def check_overtime(self):
        if self.check_out_time is None:
            return False

        schedule = self.attendance.schedule
        work_hours = schedule.get_work_hours(self.check_in_time, self.check_out_time)
        return work_hours == 0
