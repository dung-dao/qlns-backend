from rest_framework import serializers

from qlns.apps.attendance.serializers import PeriodSerializer
from qlns.apps.payroll.models import Payroll, SalaryTemplate


class PayrollSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Payroll

    template = serializers.SlugRelatedField(
        slug_field='name',
        read_only=False,
        queryset=SalaryTemplate.objects.all()
    )

    period = PeriodSerializer(read_only=True)
    confirmed_by = serializers.SlugRelatedField('full_name', read_only=True)
    require_input_file = serializers.BooleanField(read_only=True, source='is_inputs_file_required')

    def create(self, validated_data):
        modified_validated_data = validated_data
        period = self.context.get('period')
        modified_validated_data['period'] = period

        return super(PayrollSerializer, self).create(modified_validated_data)
