from django.db import transaction
from django.db.models import ProtectedError
from django.db.transaction import atomic
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.payroll.models import SalaryTemplate, SalaryTemplateField
from qlns.apps.payroll.serializers.salary_template_field_serializer import SalaryTemplateFieldSerializer
from qlns.apps.payroll.serializers.salary_template_serializer import SalaryTemplateSerializer


class SalaryTemplateView(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin
):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SalaryTemplateSerializer
    queryset = SalaryTemplate.objects.prefetch_related('fields').all()

    @action(detail=False, methods=['get'])
    def get_system_fields(self, request):
        system_fields = SalaryTemplateField.objects.filter(
            type=SalaryTemplateField.SalaryFieldType.SystemField
        )
        list_serializer = SalaryTemplateFieldSerializer(system_fields, many=True)
        return Response(data=list_serializer.data)

    @atomic
    def update(self, request, pk=None):
        template = SalaryTemplate.objects.filter(pk=pk) \
            .prefetch_related('payrolls') \
            .first()
        if template is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if template.payrolls \
                .filter(status='Confirmed') \
                .exists():
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Denied")

        serializer = self.serializer_class(instance=template, data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
        serializer.save()

        try:
            for p in template.payrolls.all():
                p.calculate_salary()
        except Exception:
            transaction.set_rollback(True)
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid template")

        return Response(data=serializer.data)

    def destroy(self, request, *args, **kwargs):
        try:
            super(SalaryTemplateView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Denied")
