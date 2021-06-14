from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from qlns.apps.attendance.serializers.attendance import EmployeeWithAttendanceSerializer
from qlns.apps.core.models import Employee
from qlns.utils.constants import MIN_UTC_DATETIME, MAX_UTC_DATETIME
from qlns.utils.datetime_utils import parse_iso_datetime


class ManageAttendanceView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    un_authorized = {
        "detail": "You do not have permission to perform this action."
    }

    def list(self, request):
        if not request.user.has_perm('attendance.view_attendance'):
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)

        employee_attendance = Employee.objects.all().prefetch_related("attendance")
        employee_attendance = filter(lambda e: e.job_history.exists(), employee_attendance)

        query_params = self.request.query_params

        start_date = parse_iso_datetime(query_params.get("from_date", None), MIN_UTC_DATETIME)
        end_date = parse_iso_datetime(query_params.get("to_date", None), MAX_UTC_DATETIME)

        context = {
            "start_date": start_date,
            "end_date": end_date,
            "period_id": self.request.query_params.get('period_id', None),
            "request": request
        }

        serializer = EmployeeWithAttendanceSerializer(employee_attendance, many=True, context=context)

        return Response(data=serializer.data)
