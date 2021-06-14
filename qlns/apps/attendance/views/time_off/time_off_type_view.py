from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from qlns.apps.attendance.models import TimeOffType
from qlns.apps.attendance.serializers import TimeOffTypeSerializer


class TimeOffTypeView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = TimeOffTypeSerializer
    queryset = TimeOffType.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            return super(TimeOffTypeView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Delete referenced record not allowed"}
            )
