from rest_framework import viewsets, permissions

from qlns.apps.payroll.models import Payslip
from qlns.apps.payroll.serializers.payslip_serializer import PayslipSerializer


class PayrollPayslipsView(viewsets.ReadOnlyModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(payroll=self.kwargs['payroll_pk'])
