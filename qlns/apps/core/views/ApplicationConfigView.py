from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from qlns.apps.core.models import ApplicationConfig
from qlns.apps.core.serializers import ApplicationConfigSerializer


class ApplicationConfigView(viewsets.ViewSet):
    def list(self, request):
        obj = ApplicationConfig.objects.first()
        if obj is None:
            Response(status=status.HTTP_400_BAD_REQUEST, data="System not fully initialized")
        return Response(data=ApplicationConfigSerializer(obj).data)

    def create(self, request):
        obj = ApplicationConfig.objects.first()
        serializer = ApplicationConfigSerializer(data=request.data, instance=obj)

        if serializer.is_valid():
            serializer.save()

        return Response(data=serializer.data)
