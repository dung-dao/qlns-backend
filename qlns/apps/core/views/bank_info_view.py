from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from qlns.apps.authentication.permissions import RWPermissionOrIsOwner
from qlns.apps.core import models as core_models
from qlns.apps.core import serializers as core_serializers


class BankInfoView(viewsets.ViewSet):
    serializer_class = core_serializers.BankInfoSerializer
    permission_classes = (RWPermissionOrIsOwner,)

    def get_queryset(self):
        try:
            return core_models.BankInfo.objects.filter(owner=self.kwargs['employee_pk'])
        except ValueError:
            return core_models.BankInfo.objects.none()

    def list(self, request, employee_pk=None):
        info = self.get_queryset().first()
        if info is not None:
            serializer = self.serializer_class(instance=info)
            return Response(data=serializer.data)
        else:
            return Response(data={})

    def create(self, request, employee_pk=None):
        info = self.get_queryset().first()

        serializer = None
        if info is None:
            serializer = self.serializer_class(data=request.data)
        else:
            serializer = self.serializer_class(
                instance=info, data=request.data)

        if serializer.is_valid():
            if str(request.data['owner']) != employee_pk:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
