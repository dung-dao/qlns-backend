from django.db import models


class TimeOff(models.Model):
    class TimeOffStatus(models.TextChoices):
        Pending = 'Pending'
        Canceled = 'Canceled'
        Approved = 'Approved'
        Rejected = 'Rejected'

    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE,
                              related_name='TimeOff')
    reviewed_by = models.ForeignKey(to='core.Employee', on_delete=models.SET_NULL,
                                    null=True, related_name='ReviewedTimeOff')

    schedule = models.ForeignKey(to='Schedule', on_delete=models.PROTECT)
    time_off_type = models.ForeignKey(to='TimeOffType', on_delete=models.PROTECT,
                                      related_name='TimeOff')

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    work_hours = models.FloatField()

    status = models.CharField(max_length=15, choices=TimeOffStatus.choices)
    note = models.TextField(blank=True, null=True)

    def calculate_work_hours(self):
        self.work_hours = self.schedule.get_work_hours(self.start_date, self.end_date)

    def trim_work_hours(self, start_time, end_time):
        start = max(start_time, self.start_date)
        end = min(end_time, self.end_date)

        return self.schedule.get_work_hours(start, end)
