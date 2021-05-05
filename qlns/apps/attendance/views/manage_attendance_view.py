from datetime import datetime

import pytz
from rest_framework.response import Response
from rest_framework.views import APIView

from qlns.apps.attendance.serializers.attendance import EmployeeWithAttendanceSerializer
from qlns.apps.core.models import Employee


class AttendanceEmployeeSerializer:
    first_name = ""
    last_name = ""


class ManageAttendanceView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        employee_attendance = Employee.objects.all().prefetch_related("attendance")
        employee_attendance = filter(lambda e: e.job_history.exists(), employee_attendance)

        query_params = self.request.query_params
        query = {
            "start_date": query_params.get('start_date', datetime.min).replace(tzinfo=pytz.utc),
            "end_date": query_params.get('end_date', datetime.max).replace(tzinfo=pytz.utc)
        }

        serializer = EmployeeWithAttendanceSerializer(employee_attendance, many=True, context=query)

        return Response(data=serializer.data)
