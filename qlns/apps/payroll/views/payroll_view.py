from rest_framework import permissions
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.payroll.models import Payroll
from qlns.apps.payroll.serializers.payroll_serializer import PayrollSerializer


class PayrollView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PayrollSerializer
    queryset = Payroll.objects.all()

    @action(detail=True, methods=['post'])
    def calculate(self, request, pk):

        payroll = Payroll.objects.filter(pk=pk).first()
        payroll.calculate_salary()

        return Response()
