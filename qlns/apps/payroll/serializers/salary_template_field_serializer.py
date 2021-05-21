from rest_framework import serializers

from qlns.apps.payroll.models import SalaryTemplateField, SalarySystemField


class SalaryTemplateFieldSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('template', 'id',)
        model = SalaryTemplateField

    def validate(self, attrs):
        field_type = attrs.get('type')
        field_code_name = attrs.get('code_name')

        if field_type is SalaryTemplateField.SalaryFieldType.SystemField:
            valid_system_field = SalarySystemField.objects \
                .filter(code_name=field_code_name) \
                .first()

            if valid_system_field is None:
                raise serializers.ValidationError('System field not exists')

            if valid_system_field.datatype != attrs.get('datatype'):
                raise serializers.ValidationError('Inconsistent system field datatype')

        elif field_type == SalaryTemplateField.SalaryFieldType.Formula:
            if attrs.get('define', None) is None:
                raise serializers.ValidationError('Formula not defined')
        return attrs
