from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from qlns.apps.payroll.models import Payslip
from qlns.apps.payroll.serializers.payslip_serializer import PayslipSerializer


class PayrollPayslipsView(viewsets.ReadOnlyModelViewSet):
    queryset = Payslip.objects.all()
    serializer_class = PayslipSerializer
    permission_classes = (permissions.IsAuthenticated,)

    un_authorized = {
        "detail": "You do not have permission to perform this action."
    }

    def get_queryset(self):
        return self.queryset.filter(payroll=self.kwargs['payroll_pk'])

    def list(self, request, *args, **kwargs):
        if not request.user.has_perm('payroll.view_payslip'):
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)
        else:
            return super(PayrollPayslipsView, self).list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if not request.user.has_perm('payroll.view_payslip'):
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)
        else:
            return super(PayrollPayslipsView, self).retrieve(request, *args, **kwargs)
