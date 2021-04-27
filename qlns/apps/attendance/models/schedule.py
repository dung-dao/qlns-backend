from functools import reduce

import pytz
from django.db import models


class Schedule(models.Model):
    TimeZone = models.TextChoices('TimeZone', reduce(lambda a, b: f'{a} {b}', pytz.all_timezones))
    name = models.CharField(max_length=100, unique=True)
    time_zone = models.CharField(max_length=100, default='Asia/Ho_Chi_Minh', choices=TimeZone.choices)

    def get_work_day(self, weekday):
        week_days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        return self.workdays.filter(day=week_days[weekday]).first()
