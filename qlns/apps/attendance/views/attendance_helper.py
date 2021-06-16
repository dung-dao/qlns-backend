from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from qlns.apps.attendance.models import Attendance
from qlns.apps.attendance.serializers.attendance.attendance_helper_serializer import AttendanceHelperSerializer
from qlns.utils.datetime_utils import local_now


class AttendanceHelper(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        result = {
            "next_step": 'clock in',
            "first_clock_in": None,
            "last_clock_out": None,
            "last_action": None,
            "last_action_at": None,
            "location": None
        }

        try:
            employee = getattr(request.user, 'employee')

            # Location
            result["location"] = employee.get_job_location()
        except ObjectDoesNotExist:
            result['next_step'] = None
            serializer = AttendanceHelperSerializer(instance=result)
            return Response(data=serializer.data)

        # Get today attendance
        today = local_now()
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

        attendance = Attendance.objects \
            .filter(Q(date__gte=today_start) &
                    Q(date__lte=today_end) &
                    Q(owner=employee)) \
            .order_by('-date') \
            .first()

        # No attendance => Return default
        if attendance is None:
            return Response(data=result)

        # Get data
        first_clock_in_tracker = attendance.tracking_data \
            .filter(check_in_time__isnull=False) \
            .order_by('check_in_time').first()

        last_tracker = attendance.tracking_data.order_by('-check_in_time').first()

        last_clock_out_tracker = attendance.tracking_data \
            .filter(check_out_time__isnull=False) \
            .order_by('-check_in_time').first()

        # Blank attendance => Return default result
        if last_tracker is None:
            return Response(data=result)

        # Next step
        if last_tracker.check_out_time is None:
            result['next_step'] = 'clock out'
        else:
            result['next_step'] = 'clock in'

        # First clock in
        if first_clock_in_tracker is not None:
            result['first_clock_in'] = first_clock_in_tracker.check_in_time
        else:
            result['first_clock_in'] = None

        # Last clock out
        if last_clock_out_tracker is not None:
            result['last_clock_out'] = last_clock_out_tracker.check_out_time
        else:
            result['last_clock_out'] = None

        # Last action
        result['last_action'] = 'clock out' \
            if last_tracker.check_out_time is not None else 'clock in'

        result['last_action_at'] = last_tracker.check_out_time \
            if last_tracker.check_out_time is not None else last_tracker.check_in_time

        # Return result
        serializer = AttendanceHelperSerializer(instance=result)
        return Response(data=serializer.data)
