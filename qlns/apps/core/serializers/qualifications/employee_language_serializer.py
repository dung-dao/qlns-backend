from rest_framework import serializers

from qlns.apps.core import models as core_models


class EmployeeLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.EmployeeLanguage
        fields = '__all__'

    owner = serializers.PrimaryKeyRelatedField(read_only=True)
    language = serializers.SlugRelatedField('name', read_only=False, queryset=core_models.Language.objects.all())
