from rest_framework import serializers

from qlns.apps.core.models import Dependent


class DependentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dependent
        fields = '__all__'
