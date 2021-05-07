from rest_framework.response import Response
from rest_framework.views import APIView

from qlns.apps.attendance.serializers.attendance import EmployeeWithAttendanceSerializer
from qlns.apps.core.models import Employee
from qlns.utils.constants import MIN_UTC_DATETIME, MAX_UTC_DATETIME
from qlns.utils.datetime_utils import parse_iso_datetime


class AttendanceEmployeeSerializer:
    first_name = ""
    last_name = ""


class ManageAttendanceView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        employee_attendance = Employee.objects.all().prefetch_related("attendance")
        employee_attendance = filter(lambda e: e.job_history.exists(), employee_attendance)

        query_params = self.request.query_params

        start_date = parse_iso_datetime(query_params.get("from_date", None), MIN_UTC_DATETIME)
        end_date = parse_iso_datetime(query_params.get("to_date", None), MAX_UTC_DATETIME)

        query = {
            "start_date": start_date,
            "end_date": end_date
        }

        serializer = EmployeeWithAttendanceSerializer(employee_attendance, many=True, context=query)

        return Response(data=serializer.data)
