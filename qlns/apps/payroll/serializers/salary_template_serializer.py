from rest_framework import serializers

from qlns.apps.payroll.models import SalaryTemplate, SalaryTemplateField
from qlns.apps.payroll.serializers.salary_template_field_serializer import SalaryTemplateFieldSerializer


class SalaryTemplateSerializer(serializers.ModelSerializer):
    fields = SalaryTemplateFieldSerializer(many=True, read_only=False)
    can_be_modified = serializers.BooleanField(source='is_modifiable', read_only=True)

    class Meta:
        fields = '__all__'
        model = SalaryTemplate

    def create(self, validated_data):
        fields = validated_data.pop('fields')

        template = SalaryTemplate(**validated_data)
        template.save()

        for f in fields:
            field = SalaryTemplateField(**f)
            field.template = template
            field.save()
        return template

    def update(self, instance, validated_data):
        fields = validated_data.pop('fields')
        instance.fields.all().delete()

        for key in validated_data.keys():
            setattr(instance, key, validated_data.get(key, getattr(instance, key)))

        instance.save()

        for f in fields:
            field = SalaryTemplateField(**f)
            field.template = instance
            field.save()

        return instance
