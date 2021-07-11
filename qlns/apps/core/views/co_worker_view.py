from rest_framework import permissions
from rest_framework.viewsets import ReadOnlyModelViewSet

from qlns.apps.core.models import Employee
from qlns.apps.core.serializers.public_employee_serializer import PublicEmployeeSerializer


class CoWorkerView(ReadOnlyModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Employee.objects.all()
    serializer_class = PublicEmployeeSerializer
