from rest_framework import viewsets

from qlns.apps.authentication.permissions import RWPermissionOrIsOwner
from qlns.apps.payroll.models import Payslip
from qlns.apps.payroll.serializers.payslip_serializer import PayslipSerializer


class MyPayslipView(viewsets.ReadOnlyModelViewSet):
    serializer_class = PayslipSerializer
    queryset = Payslip.objects.all()
    permission_classes = (RWPermissionOrIsOwner,)

    def get_queryset(self):
        return self.queryset.filter(owner=self.kwargs.get('employee_pk'))
