from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from qlns.apps.attendance.models import Schedule
from qlns.apps.attendance.serializers import ScheduleSerializer


class ScheduleView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
