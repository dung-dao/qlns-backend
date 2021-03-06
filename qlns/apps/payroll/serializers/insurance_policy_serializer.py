from rest_framework import serializers

from qlns.apps.payroll.models import InsurancePolicy


class InsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePolicy
        fields = '__all__'
