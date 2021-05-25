from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from qlns.apps.core import serializers as core_serializers
from qlns.apps.core import models as core_models
from rest_framework import permissions


class DepartmentView(viewsets.ModelViewSet):
    serializer_class = core_serializers.DepartmentSerializer
    queryset = core_models.Department.objects.all()
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)

    def create(self, request, *args, **kwargs):
        try:
            return super(DepartmentView, self).create(request)
        except core_serializers.MultiRootException:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Multiple root department")

    def update(self, request, pk=None):
        try:
            super(DepartmentView, self).update(request, pk)
            return Response()
        except core_serializers.CycleParentException:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Cycle Parent Department")
