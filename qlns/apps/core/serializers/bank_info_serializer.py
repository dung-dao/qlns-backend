from rest_framework import serializers

from qlns.apps.core import models as core_models


class BankInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = core_models.BankInfo
        fields = '__all__'
