from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from qlns.apps.authentication.permissions import RWPermissionOrReadOnly
from qlns.apps.payroll.models import PayrollConfig
from qlns.apps.payroll.serializers import PayrollConfigSerializer


class PayrollConfigView(viewsets.ViewSet):
    permission_classes = (RWPermissionOrReadOnly,)
    serializer_class = PayrollConfigSerializer

    queryset = PayrollConfig.objects.all()

    def get_config(self):
        return self.queryset.first()

    def list(self, request):
        serializer = PayrollConfigSerializer(instance=self.get_config())
        return Response(data=serializer.data)

    def create(self, request):
        serializer = PayrollConfigSerializer(instance=self.get_config(), data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
