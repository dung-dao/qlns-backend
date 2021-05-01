from rest_framework import serializers

from qlns.apps.payroll.models import TaxPolicy


class TaxPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxPolicy
        fields = '__all__'
