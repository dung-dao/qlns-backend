from django.db import models
from django.utils import timezone


class Holiday(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    schedule = models.ForeignKey(to='Schedule', on_delete=models.PROTECT)

    def trim_work_hours(self, start_time, end_time):

        start = max(start_time, self.start_date)
        end = min(end_time, self.end_date)

        start = timezone.localtime(start)
        end = timezone.localtime(end)

        if start >= end:
            return 0.0
        else:
            duration = end - start
            days = duration.days
            seconds = duration.seconds
            hours = days * 24 + seconds / 3600
            return round(hours, 1)
