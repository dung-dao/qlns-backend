from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from qlns.apps.payroll.models import PayrollConfig
from qlns.apps.payroll.serializers import PayrollConfigSerializer


class PayrollConfigView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = PayrollConfigSerializer

    def get_config(self):
        return PayrollConfig.objects.first()

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
