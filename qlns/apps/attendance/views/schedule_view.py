from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from qlns.apps.attendance.models import Schedule
from qlns.apps.attendance.serializers import ScheduleSerializer


class ScheduleView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            super(ScheduleView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Delete referenced record not allowed"}
            )
