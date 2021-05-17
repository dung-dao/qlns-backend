from rest_framework import serializers

from qlns.apps.job import models as job_models


class TerminationSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(read_only=True)
    reason = serializers.SlugRelatedField(
        slug_field="name",
        read_only=False,
        queryset=job_models.TerminationReason.objects.all()
    )

    class Meta:
        model = job_models.Termination
        exclude = ("id",)

    def create(self, validated_data):
        modified_data = validated_data
        job = self.context.get("job")
        modified_data["job"] = job
        return super(TerminationSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        raise Exception('unreachable code')
