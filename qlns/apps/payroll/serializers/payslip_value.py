from rest_framework import serializers

from qlns.apps.payroll.models import PayslipValue
from qlns.apps.payroll.serializers.salary_template_field_serializer import SalaryTemplateFieldSerializer


class PayslipValueSerializer(serializers.ModelSerializer):
    field = SalaryTemplateFieldSerializer(read_only=True)

    class Meta:
        model = PayslipValue
        exclude = ('id', 'payslip')
