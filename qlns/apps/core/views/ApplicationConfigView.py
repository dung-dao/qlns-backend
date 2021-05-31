from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from qlns.apps.authentication.permissions import RWPermissionOrReadOnly
from qlns.apps.core.models import ApplicationConfig
from qlns.apps.core.serializers import ApplicationConfigSerializer


class ApplicationConfigView(viewsets.ViewSet):
    permission_classes = (RWPermissionOrReadOnly,)

    queryset = ApplicationConfig.objects.all()

    def list(self, request):
        obj = self.queryset.first()
        if obj is None:
            Response(status=status.HTTP_400_BAD_REQUEST, data="System not fully initialized")
        return Response(data=ApplicationConfigSerializer(obj).data)

    def create(self, request):
        obj = self.queryset.first()
        serializer = ApplicationConfigSerializer(data=request.data, instance=obj)

        if serializer.is_valid():
            serializer.save()

        return Response(data=serializer.data)
