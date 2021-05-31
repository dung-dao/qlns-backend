from rest_framework import serializers

from qlns.apps.core import models as core_models
from qlns.apps.core.models import Employee


class EmployeeSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.EmployeeSkill
        fields = '__all__'

    owner = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Employee.objects.all())
    skill = serializers.SlugRelatedField('name', read_only=False, queryset=core_models.Skill.objects.all())
