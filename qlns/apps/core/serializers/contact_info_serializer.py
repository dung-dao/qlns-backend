from rest_framework import serializers
from qlns.apps.core import models as core_models


class ContactInfoSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(
        queryset=core_models.Employee.objects.all())
    country = serializers.SlugRelatedField(
        slug_field='name',
        queryset=core_models.Country.objects.all(),
        allow_null=True, required=False)

    class Meta:
        model = core_models.ContactInfo
        fields = '__all__'
