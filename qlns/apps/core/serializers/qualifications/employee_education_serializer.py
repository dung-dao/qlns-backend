from rest_framework import serializers

from qlns.apps.core import models as core_models
from qlns.apps.core.models import Employee


class EmployeeEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.EmployeeEducation
        fields = '__all__'

    owner = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Employee.objects.all())
    education_level = serializers.SlugRelatedField('name', read_only=False,
                                                   queryset=core_models.EducationLevel.objects.all())
