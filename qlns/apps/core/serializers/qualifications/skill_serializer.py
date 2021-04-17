from rest_framework import serializers
from qlns.apps.core import models as core_models


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.Skill
        fields = '__all__'
