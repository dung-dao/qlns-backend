from rest_framework import serializers

from qlns.apps.payroll.models import Payslip
from qlns.apps.payroll.serializers.payslip_value import PayslipValueSerializer


class PayslipSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = Payslip

    def get_values(self, instance):
        values = instance.values.all().order_by('field__index')
        return PayslipValueSerializer(values, many=True).data
