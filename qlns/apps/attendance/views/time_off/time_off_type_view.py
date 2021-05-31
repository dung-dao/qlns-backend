from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from qlns.apps.attendance.models import TimeOffType
from qlns.apps.attendance.serializers import TimeOffTypeSerializer


class TimeOffTypeView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = TimeOffTypeSerializer
    queryset = TimeOffType.objects.all()
