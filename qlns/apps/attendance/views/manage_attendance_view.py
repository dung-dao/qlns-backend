from datetime import datetime

import pytz
from dateutil.parser import isoparse
from django.utils import timezone
from rest_framework import status
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

        try:
            from_date_str = query_params.get('start_date', None)
            to_date_str = query_params.get('end_date', None)

            start_date = isoparse(from_date_str) if from_date_str is not None \
                else datetime.min.replace(tzinfo=pytz.utc)
            end_date = isoparse(to_date_str) if to_date_str is not None \
                else datetime.max.replace(tzinfo=pytz.utc)

            if timezone.is_naive(start_date) or timezone.is_naive(end_date):
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad query params")
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Bad query params")

        query = {
            "start_date": start_date,
            "end_date": end_date
        }

        serializer = EmployeeWithAttendanceSerializer(employee_attendance, many=True, context=query)

        return Response(data=serializer.data)
