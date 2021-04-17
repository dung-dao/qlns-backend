from rest_framework import serializers

from qlns.apps.core import models as core_models


class EmployeeEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.EmployeeEducation
        fields = '__all__'

    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    education_level = serializers.SlugRelatedField('name', read_only=False, queryset=core_models.EducationLevel.objects.all())
