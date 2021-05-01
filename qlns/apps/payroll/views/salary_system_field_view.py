from rest_framework import permissions
from rest_framework import viewsets, mixins

from qlns.apps.payroll.models import SalarySystemField
from qlns.apps.payroll.serializers.salary_system_field_serializer import SalarySystemFieldSerializer


class SalarySystemFieldView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SalarySystemFieldSerializer
    queryset = SalarySystemField.objects.all()
