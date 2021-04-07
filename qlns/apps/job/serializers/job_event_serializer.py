from rest_framework import serializers

from qlns.apps.job.models import JobEvent


class JobEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobEvent
        fields = '__all__'
