from rest_framework import serializers

from qlns.apps.core.models import Employee
from qlns.apps.payroll.models import EmployeeSalary, InsurancePolicy, TaxPolicy


class EmployeeSalarySerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    insurance_policy = serializers.SlugRelatedField(
        slug_field="name",
        queryset=InsurancePolicy.objects.all()
    )
    tax_policy = serializers.SlugRelatedField(
        slug_field="name",
        queryset=TaxPolicy.objects.all()
    )

    class Meta:
        model = EmployeeSalary
        fields = '__all__'

    def create(self, validated_data):
        modified_validated_data = validated_data
        request = self.context['request']
        owner = self.context['owner']
        modified_validated_data['owner'] = owner

        return super(EmployeeSalarySerializer, self).create(modified_validated_data)
