from rest_framework import serializers

from qlns.apps.payroll.models import Payroll, SalaryTemplate
from qlns.apps.payroll.serializers.payslip_serializer import PayslipSerializer


class PayrollSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Payroll

    # payslips = PayslipSerializer(many=True, read_only=True)
    template = serializers.SlugRelatedField(
        slug_field='name',
        read_only=False,
        queryset=SalaryTemplate.objects.all()
    )
