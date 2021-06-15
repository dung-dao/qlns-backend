import formulas
from formulas.errors import FormulaError
from rest_framework import serializers
from schedula import DispatcherError

from qlns.apps.payroll.models import SalaryTemplate, SalaryTemplateField, SalarySystemField
from qlns.apps.payroll.models.payroll_utils import PIT_VN
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

    def validate(self, attrs):
        functions = formulas.get_functions()
        functions['PIT_VN'] = PIT_VN

        fields = attrs.get('fields', [])
        fields.sort(key=lambda e: e['index'])

        system_fields = SalarySystemField.objects.all()

        test_calculation_dict = {}
        for sf in system_fields:
            if sf.datatype == 'Text':
                test_calculation_dict[sf.code_name] = 'a'
            elif sf.datatype in ['Number', 'Currency', ]:
                test_calculation_dict[sf.code_name] = 7

        for index in range(len(fields)):
            field = fields[index]
            if field['type'] == 'System Field':
                if field['datatype'] == 'Text':
                    test_calculation_dict[field['code_name']] = 'a'
                elif field['datatype'] in ['Number', 'Currency', ]:
                    test_calculation_dict[field['code_name']] = 7
            elif field['type'] == 'Formula':
                try:
                    formula = formulas.Parser().ast(f'={field["define"]}')[1].compile()

                    # create context
                    formula_context = {}
                    inputs = formula.inputs
                    for key in test_calculation_dict:
                        if key.upper() in inputs:
                            formula_context[key.upper()] = test_calculation_dict[key]

                    # Try calculating
                    ans = formula(**formula_context)

                    # validate datatype
                    if field['datatype'] == 'Text':
                        ans = str(ans)
                    elif field['datatype'] in ['Number', 'Currency', ]:
                        ans = float(ans)

                    test_calculation_dict[field["code_name"]] = ans

                except (FormulaError,) as e:
                    raise serializers.ValidationError({"fields": f'error at <{field["code_name"]}> : {str(e)}'})
                except TypeError as e:
                    raise serializers.ValidationError(
                        {"fields": f'formula <{field["code_name"]}> {str(e)}'})
                except ValueError as e:
                    raise serializers.ValidationError(f'Invalid $datatype$ at <{field["code_name"]}> : {str(e)}')
                except DispatcherError:
                    raise serializers.ValidationError(f'$Undefined function$ at <{field["code_name"]}>')
        return attrs
