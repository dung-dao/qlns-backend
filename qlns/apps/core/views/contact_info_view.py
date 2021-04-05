from rest_framework import viewsets

from qlns.apps.core import models as core_models
from qlns.apps.core import serializers as core_serializers

from rest_framework.response import Response
from rest_framework import status


class ContactInfoView(viewsets.ViewSet):
    serializer_class = core_serializers.ContactInfoSerializer

    def get_queryset(self):
        return core_models.ContactInfo.objects.filter(owner=self.kwargs['employee_pk'])

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