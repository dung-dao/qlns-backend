from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.attendance.models import Period
from qlns.apps.payroll.models import Payroll
from qlns.apps.payroll.serializers.payroll_serializer import PayrollSerializer


class PayrollView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PayrollSerializer
    queryset = Payroll.objects.all()

    def create(self, request, *args, **kwargs):
        ctx = {"request": request, "period": request.data.get('period', None)}
        if ctx['period'] is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="period required")

        period = get_object_or_404(Period, pk=ctx['period'])
        ctx['period'] = period

        serializer = PayrollSerializer(data=request.data, context=ctx)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def calculate(self, request, pk):
        payroll = Payroll.objects.filter(pk=pk).first()
        payroll.calculate_salary()

        return Response()
