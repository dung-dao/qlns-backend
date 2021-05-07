from datetime import timedelta, datetime

from django.db import models
from django.utils import timezone

from qlns.utils.constants import MAX_UTC_DATETIME


class Schedule(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def get_work_day(self, weekday):
        week_days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
        return self.workdays.filter(day=week_days[weekday]).first()

    def shift_workday(self, to_date, weekday):
        workday = self.get_work_day(weekday)

        if workday is None:
            return None

        date_params = {
            "year": to_date.year,
            "month": to_date.month,
            "day": to_date.day
        }

        weekday = workday.day
        morning_from = timezone.localtime(workday.morning_from) \
            .replace(**date_params) if workday.morning_from is not None else None

        morning_to = timezone.localtime(workday.morning_to) \
            .replace(**date_params) if workday.morning_to is not None else None

        afternoon_from = timezone.localtime(workday.afternoon_from) \
            .replace(**date_params) if workday.afternoon_from is not None else None

        afternoon_to = timezone.localtime(workday.afternoon_to) \
            .replace(**date_params) if workday.afternoon_to is not None else None

        workday_dict = {"weekday": weekday, }
        if morning_from is not None:
            workday_dict['morning_from'] = morning_from

        if morning_to is not None:
            workday_dict['morning_to'] = morning_to

        if afternoon_from is not None:
            workday_dict['afternoon_from'] = afternoon_from

        if afternoon_to is not None:
            workday_dict['afternoon_to'] = afternoon_to

        return workday_dict

    def get_schedule_work_hours(self):
        today = timezone.now()
        one_week = timedelta(weeks=1)
        next_week = today + one_week

        schedule_work_hours = self.get_work_hours(today, next_week)
        return schedule_work_hours

    def get_work_hours(self, start_time, end_time):
        start_time = timezone.localtime(start_time)
        end_time = timezone.localtime(end_time)

        duration = 0.0

        i_date = start_time
        while i_date < end_time:
            weekday = i_date.weekday()
            workday_dict = self.shift_workday(i_date, weekday)

            # morning duration
            morning_start = max(workday_dict.get("morning_from", i_date), i_date)
            morning_end = min(workday_dict.get("morning_to", i_date), end_time)
            morning_hours = (morning_end - morning_start).seconds / 3600 \
                if morning_end >= morning_start else 0

            # afternoon duration
            afternoon_start = max(workday_dict.get("afternoon_from", i_date), i_date)
            afternoon_end = min(workday_dict.get("afternoon_to", i_date), end_time)
            afternoon_hours = (afternoon_end - afternoon_start).seconds / 3600 \
                if afternoon_end >= afternoon_start else 0

            duration += morning_hours + afternoon_hours

            # Shift i_date to work date
            next_day = i_date + timedelta(days=1)
            while self.shift_workday(next_day, next_day.weekday()) is None:
                next_day += timedelta(days=1)

            next_work_day_dict = self.shift_workday(next_day, next_day.weekday())

            i_date = min(
                next_work_day_dict.get("morning_from", MAX_UTC_DATETIME),
                next_work_day_dict.get("afternoon_from", MAX_UTC_DATETIME),
            )

        return duration
