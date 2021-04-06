from rest_framework import serializers
from qlns.apps.job import models as job_models


class WorkShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = job_models.WorkShift
        fields = '__all__'
