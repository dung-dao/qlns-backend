from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from qlns.apps.job import models as job_models
from qlns.apps.job import serializers as job_serializers


class LocationView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = job_serializers.LocationSerializer
    queryset = job_models.Location.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            return super(LocationView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Delete referenced record not allowed"}
            )
