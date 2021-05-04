from functools import reduce

import pytz
from django.db import models


class ApplicationConfig(models.Model):
    TimeZone = models.TextChoices('TimeZone', reduce(lambda a, b: f'{a} {b}', pytz.all_timezones))

    # Properties
    time_zone = models.CharField(max_length=255, default='Asia/Ho_Chi_Minh', choices=TimeZone.choices)
