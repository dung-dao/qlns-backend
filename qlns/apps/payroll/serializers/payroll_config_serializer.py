from rest_framework import serializers

from qlns.apps.payroll.models import PayrollConfig


class PayrollConfigSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            'use_check_in',
            'monthly_start_date',
        )
        model = PayrollConfig
