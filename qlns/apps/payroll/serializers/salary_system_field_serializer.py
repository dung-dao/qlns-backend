from rest_framework import serializers

from qlns.apps.payroll.models import SalarySystemField


class SalarySystemFieldSerializer(serializers.ModelSerializer):
    code_name = serializers.CharField(read_only=True)

    class Meta:
        model = SalarySystemField
        fields = '__all__'
