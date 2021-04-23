from rest_framework import viewsets

from qlns.apps.attendance.models import Schedule
from qlns.apps.attendance.serializers import ScheduleSerializer


class ScheduleView(viewsets.ModelViewSet):
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
