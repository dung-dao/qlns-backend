from datetime import timedelta

import pytz
from django.db import models


class Holiday(models.Model):
    name = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    work_hours = models.FloatField(default=0)

    schedule = models.ForeignKey(to='Schedule', on_delete=models.PROTECT)

    def calculate_work_hours(self):
        locale_start_date = self.start_date.astimezone(pytz.timezone(self.schedule.time_zone))
        locale_end_date = self.end_date.astimezone(pytz.timezone(self.schedule.time_zone))

        duration = 0.0
        i_date = locale_start_date
        while i_date <= locale_end_date:
            weekday = i_date.weekday()
            workday = self.schedule.get_locale_workday(i_date, weekday)

            if workday is None:
                i_date = i_date + timedelta(days=1)
                continue

            morning_start = max(workday["morning_from"], i_date) \
                if workday["morning_from"] is not None else i_date
            morning_end = min(workday["morning_to"], locale_end_date) \
                if workday["morning_to"] is not None else i_date

            morning_hours = (morning_end - morning_start).seconds / 3600 \
                if morning_end >= morning_start else 0

            afternoon_start = max(workday["afternoon_from"], i_date) \
                if workday["afternoon_from"] is not None else i_date
            afternoon_end = min(workday["afternoon_to"], locale_end_date) \
                if workday["afternoon_to"] is not None else i_date

            afternoon_hours = (afternoon_end - afternoon_start).seconds / 3600 \
                if afternoon_end >= afternoon_start else 0

            duration = duration + morning_hours + afternoon_hours

            i_date = i_date + timedelta(days=1)

        self.work_hours = duration
