from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.payroll.models import SalaryTemplate, SalaryTemplateField
from qlns.apps.payroll.serializers.salary_template_field_serializer import SalaryTemplateFieldSerializer
from qlns.apps.payroll.serializers.salary_template_serializer import SalaryTemplateSerializer


class SalaryTemplateView(viewsets.ModelViewSet):
    serializer_class = SalaryTemplateSerializer
    queryset = SalaryTemplate.objects.prefetch_related('fields').all()

    @action(detail=False, methods=['get'])
    def get_system_fields(self, request):
        system_fields = SalaryTemplateField.objects.filter(
            type=SalaryTemplateField.SalaryFieldType.SystemField
        )
        list_serializer = SalaryTemplateFieldSerializer(system_fields, many=True)
        return Response(data=list_serializer.data)
