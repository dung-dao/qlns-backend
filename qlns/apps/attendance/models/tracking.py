import pytz
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
        # Scheduled time
        schedule = self.attendance.schedule

        # Locale time
        locale_check_in_time = self.check_in_time.astimezone(pytz.timezone(schedule.time_zone))
        locale_check_out_time = self.check_out_time.astimezone(pytz.timezone(schedule.time_zone))

        weekday = locale_check_in_time.weekday()
        workday = schedule.get_work_day(weekday)

        locale_schedule = {
            "morning_from": workday.morning_from.astimezone(pytz.timezone(schedule.time_zone)).replace(
                year=locale_check_in_time.year,
                month=locale_check_in_time.month,
                day=locale_check_in_time.day),
            "morning_to": workday.morning_to.astimezone(pytz.timezone(schedule.time_zone)).replace(
                year=locale_check_in_time.year,
                month=locale_check_in_time.month,
                day=locale_check_in_time.day),
            "afternoon_from": workday.afternoon_from.astimezone(pytz.timezone(schedule.time_zone)).replace(
                year=locale_check_in_time.year,
                month=locale_check_in_time.month,
                day=locale_check_in_time.day),
            "afternoon_to": workday.afternoon_to.astimezone(pytz.timezone(schedule.time_zone)).replace(
                year=locale_check_in_time.year,
                month=locale_check_in_time.month,
                day=locale_check_in_time.day),
        }

        if self.check_in_time is None or \
                self.check_out_time is None or \
                not self.is_overtime:
            return 0

        if locale_schedule["morning_from"] <= locale_check_in_time <= locale_schedule["morning_to"]:
            check_in_time = max(locale_schedule["morning_from"], locale_check_in_time)
            check_out_time = min(locale_schedule["morning_to"], locale_check_out_time)

        elif locale_schedule["afternoon_from"] <= locale_check_in_time <= locale_schedule["afternoon_to"]:
            check_in_time = max(locale_schedule["afternoon_from"], locale_check_in_time)
            check_out_time = min(locale_schedule["afternoon_to"], locale_check_out_time)
        else:
            return 0

        duration = (check_out_time - check_in_time).seconds / 3600
        return duration
