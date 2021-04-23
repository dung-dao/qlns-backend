from rest_framework import viewsets

from qlns.apps.attendance.models import OvertimeType
from qlns.apps.attendance.serializers.attendance import OvertimeTypeSerializer


class OvertimeTypeView(viewsets.ModelViewSet):
    queryset = OvertimeType.objects.all()
    serializer_class = OvertimeTypeSerializer
