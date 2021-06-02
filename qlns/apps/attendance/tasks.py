from datetime import timedelta

from django.db.transaction import atomic
from django.utils import timezone

from qlns.apps.attendance import models as attendance_models
from qlns.apps.core.models import ApplicationConfig


@atomic
def auto_checkout():
    not_checked_out_trackers = attendance_models.Tracking.objects.filter(check_out_time__isnull=True)
    for tracking in not_checked_out_trackers:
        # Prepare data
        attendance = tracking.attendance
        check_in_time = timezone.localtime(tracking.check_in_time)
        check_out_time = None
        schedule = tracking.attendance.schedule
        config = ApplicationConfig.objects.first()
        allowed_early_minutes = config.early_check_in_minutes

        # Calculate checkout_time
        workday = schedule.shift_workday(check_in_time, check_in_time.weekday())
        morning_from = workday.get('morning_from', timezone.datetime.max)
        morning_to = workday.get('morning_to', timezone.datetime.max)

        afternoon_from = workday.get('afternoon_from', timezone.datetime.max)
        afternoon_to = workday.get('afternoon_to', timezone.datetime.max)

        # Check if tracking is normal tracking or ot tracking
        early_timedelta = timedelta(minutes=allowed_early_minutes)
        # Morning shift
        if morning_from - early_timedelta <= check_in_time < morning_to:
            check_out_time = morning_to
        # Afternoon shift
        elif afternoon_from - early_timedelta <= check_in_time < afternoon_to:
            check_out_time = afternoon_to
        # OT
        else:
            if check_in_time < morning_from - early_timedelta:
                check_out_time = morning_from - early_timedelta - timedelta(microseconds=1)
            elif morning_to <= check_in_time < afternoon_from - early_timedelta:
                check_out_time = afternoon_from - early_timedelta - timedelta(microseconds=1)
            elif check_in_time > afternoon_to:
                check_out_time = check_in_time.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Check out
        tracking.check_out_time = check_out_time
        tracking.check_out_lat = None
        tracking.check_out_lng = None
        tracking.check_out_note = 'System Auto Check Out'
        tracking.check_out_outside = None
        tracking.check_out_image = None
        tracking.check_out_face_authorized = None

        tracking.save()
        tracking.is_overtime = tracking.check_overtime()
        tracking.save()

        # Calculate work hours
        attendance.calculate_work_hours()
        attendance.save()
