from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from qlns.apps.authentication.permissions.DjangoModelPermissionOrIsOwner import DjangoModelPermissionOrIsOwner
from qlns.apps.core import models as core_models
from qlns.apps.core.serializers import qualifications as qualification_serializers


class EmployeeEducationView(viewsets.ModelViewSet):
    serializer_class = qualification_serializers.EmployeeEducationSerializer
    permission_classes = (DjangoModelPermissionOrIsOwner,)

    def get_queryset(self):
        return core_models.EmployeeEducation.objects.filter(owner=self.kwargs['employee_pk'])

    def create(self, request, *args, **kwargs):
        if 'owner' not in request.data or str(request.data['owner']) != self.kwargs['employee_pk']:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid owner data")

        return super(self.__class__, self).create(request, *args, **kwargs)
