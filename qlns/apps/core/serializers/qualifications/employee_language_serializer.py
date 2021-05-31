from rest_framework import serializers

from qlns.apps.core import models as core_models
from qlns.apps.core.models import Employee


class EmployeeLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.EmployeeLanguage
        fields = '__all__'

    owner = serializers.PrimaryKeyRelatedField(read_only=False, queryset=Employee.objects.all())
    language = serializers.SlugRelatedField('name', read_only=False, queryset=core_models.Language.objects.all())
