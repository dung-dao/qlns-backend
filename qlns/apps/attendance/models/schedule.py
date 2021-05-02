from datetime import datetime
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

    def get_locale_workday(self, convert_date, weekday):
        locale_convert_date = convert_date.astimezone(pytz.timezone(self.time_zone))
        workday = self.get_work_day(weekday)

        if workday is None:
            return None

        locale_workday = {
            "weekday": workday.day,
            "morning_from": workday.morning_from.astimezone(pytz.timezone(self.time_zone)).replace(
                year=locale_convert_date.year,
                month=locale_convert_date.month,
                day=locale_convert_date.day) if workday.morning_from is not None else None,
            "morning_to": workday.morning_to.astimezone(pytz.timezone(self.time_zone)).replace(
                year=locale_convert_date.year,
                month=locale_convert_date.month,
                day=locale_convert_date.day) if workday.morning_to is not None else None,
            "afternoon_from": workday.afternoon_from.astimezone(pytz.timezone(self.time_zone)).replace(
                year=locale_convert_date.year,
                month=locale_convert_date.month,
                day=locale_convert_date.day) if workday.afternoon_from is not None else None,
            "afternoon_to": workday.afternoon_to.astimezone(pytz.timezone(self.time_zone)).replace(
                year=locale_convert_date.year,
                month=locale_convert_date.month,
                day=locale_convert_date.day) if workday.afternoon_to is not None else None,
        }
        return locale_workday

    def get_schedule_work_hours(self):
        work_hours = 0
        workdays = self.workdays.all()
        today = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(pytz.timezone(self.time_zone))

        for wd in workdays:
            if wd.morning_from is not None:
                morning_from = wd.morning_from.replace(
                    year=today.year,
                    month=today.month,
                    day=today.day)
                morning_to = wd.morning_to.replace(
                    year=today.year,
                    month=today.month,
                    day=today.day)
                work_hours = work_hours + (morning_to - morning_from).seconds / 3600
            if wd.afternoon_from is not None:
                afternoon_from = wd.afternoon_from.replace(
                    year=today.year,
                    month=today.month,
                    day=today.day)
                afternoon_to = wd.afternoon_to.replace(
                    year=today.year,
                    month=today.month,
                    day=today.day)
                work_hours += (afternoon_to - afternoon_from).seconds / 3600

        return work_hours
