from rest_framework import viewsets

from qlns.apps.attendance.models import TimeOffType
from qlns.apps.attendance.serializers import TimeOffTypeSerializer


class TimeOffTypeView(viewsets.ModelViewSet):
    serializer_class = TimeOffTypeSerializer
    queryset = TimeOffType.objects.all()
