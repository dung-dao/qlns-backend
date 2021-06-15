from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from qlns.apps.attendance.models import Attendance
from qlns.apps.attendance.serializers.attendance.attendance_helper_serializer import AttendanceHelperSerializer


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
        except ObjectDoesNotExist:
            result['next_step'] = None
            serializer = AttendanceHelperSerializer(instance=result)
            return Response(data=serializer.data)

        attendance = Attendance.objects \
            .filter(owner=employee) \
            .order_by('-date').first()

        # No attendance
        if attendance is None:
            return Response(data=result)
        last_tracker = attendance.tracking_data.order_by('-check_in_time').first()
        last_clock_out_tracker = attendance.tracking_data \
            .filter(check_out_time__isnull=False) \
            .order_by('-check_in_time').first()
        first_tracker = attendance.tracking_data.order_by('check_in_time').first()

        # Blank attendance
        if last_tracker is None:
            return Response(data=result)

        # Last tracking
        result['first_clock_in'] = first_tracker.check_in_time
        result['last_clock_out'] = last_clock_out_tracker.check_out_time

        result['last_action'] = 'clock out' \
            if last_tracker.check_out_time is not None else 'clock in'

        result['last_action_at'] = last_tracker.check_out_time \
            if last_tracker.check_out_time is not None else last_tracker.check_in_time

        if last_tracker.check_out_time is None:
            result['next_step'] = 'clock out'

        # Location
        result["location"] = employee.get_job_location()

        serializer = AttendanceHelperSerializer(instance=result)
        return Response(data=serializer.data)
