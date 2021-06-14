# Script to load data for testing purpose only
from django.utils import timezone

from qlns.apps.attendance import models as attendance_models
from qlns.apps.core import models as core_models
from qlns.utils.constants import MAX_UTC_DATETIME
from qlns.utils.datetime_utils import get_next_date


def create_month_attendance(employee_id, seed_date):
    period = attendance_models.Period.get_or_create(seed_date)
    employee = core_models.Employee.objects.get(pk=employee_id)
    schedule = employee.get_current_schedule()
    location = employee.get_job_location()

    assert employee is not None and location is not None and schedule is not None
    lat = location.lat
    lng = location.lng

    start_time = timezone.localtime(period.start_date)
    end_time = timezone.localtime(period.end_date)

    i_date = start_time
    while i_date < end_time:
        workday_dict = schedule.shift_workday(i_date, i_date.weekday())

        if workday_dict is None:
            while workday_dict is None:
                i_date = get_next_date(i_date)
                workday_dict = schedule.shift_workday(i_date, i_date.weekday())

            i_date = min(
                workday_dict.get("morning_from", MAX_UTC_DATETIME),
                workday_dict.get("afternoon_from", MAX_UTC_DATETIME)
            )

        if i_date >= end_time:
            break

        # prepare data
        morning_start = workday_dict.get("morning_from", None)
        morning_end = workday_dict.get("morning_to", None)
        afternoon_start = workday_dict.get("afternoon_from", None)
        afternoon_end = workday_dict.get("afternoon_to", None)

        # Create attendance
        attendance = attendance_models.Attendance(
            owner=employee,
            schedule=schedule,
            date=min(morning_start, afternoon_start),
            period=period,
            status=attendance_models.Attendance.AttendanceLogStatus.Pending
        )
        attendance.save()

        # Morning
        if morning_start is not None:
            morning_tracking = attendance_models.Tracking(
                attendance=attendance,
                check_in_time=morning_start,
                check_out_time=morning_end,

                check_in_lat=lat,
                check_out_lat=lat,

                check_in_lng=lng,
                check_out_lng=lng,

                check_in_outside=False,
                check_out_outside=False,

                location=location,
            )
            morning_tracking.save()
            morning_tracking.is_overtime = morning_tracking.check_overtime()
            morning_tracking.save()

        # Afternoon
        if afternoon_start is not None:
            morning_tracking = attendance_models.Tracking(
                attendance=attendance,
                check_in_time=afternoon_start,
                check_out_time=afternoon_end,

                check_in_lat=lat,
                check_out_lat=lat,

                check_in_lng=lng,
                check_out_lng=lng,

                check_in_outside=False,
                check_out_outside=False,

                location=location,
            )
            morning_tracking.save()
            morning_tracking.is_overtime = morning_tracking.check_overtime()
            morning_tracking.save()

        attendance.calculate_work_hours()

        print(morning_start, morning_end, afternoon_start, afternoon_end)
        i_date = get_next_date(i_date)
