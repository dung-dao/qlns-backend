from rest_framework import serializers

from qlns.apps.payroll.models import SalaryTemplateField, SalarySystemField


class SalaryTemplateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        # fields = '__all__'
        exclude = ('templates', 'id',)
        model = SalaryTemplateField

    def validate(self, attrs):
        salary_type = attrs.get('type')
        field_code_name = attrs.get('code_name')
        if salary_type != SalaryTemplateField.SalaryFieldType.SystemField:
            return attrs

        valid_system_field = SalarySystemField.objects \
            .filter(code_name=field_code_name) \
            .exists()

        if not valid_system_field:
            raise serializers.ValidationError('System field not exists')

        return attrs
