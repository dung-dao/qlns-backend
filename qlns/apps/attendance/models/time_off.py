from datetime import timedelta

import pytz
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
        start_date = self.start_date.astimezone(pytz.timezone(self.schedule.time_zone))
        end_date = self.end_date.astimezone(pytz.timezone(self.schedule.time_zone))

        duration = 0.0
        i_date = start_date
        while i_date <= end_date:
            weekday = i_date.weekday()
            workday = self.schedule.get_locale_workday(i_date, weekday)

            if workday is None:
                i_date = i_date + timedelta(days=1)
                continue

            morning_start = max(workday["morning_from"], i_date)
            morning_end = min(workday["morning_to"], end_date)

            morning_hours = (morning_end - morning_start).seconds / 3600 \
                if morning_end > morning_start else 0

            afternoon_start = max(workday["afternoon_from"], i_date)
            afternoon_end = min(workday["afternoon_to"], end_date)

            afternoon_hours = (afternoon_end - afternoon_start).seconds / 3600 \
                if afternoon_end >= afternoon_start else 0

            duration = duration + morning_hours + afternoon_hours

            i_date = i_date + timedelta(days=1)

        self.work_hours = duration
