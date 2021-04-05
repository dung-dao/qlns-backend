from rest_framework import serializers

from qlns.apps.core import models as core_models


class CycleParentException(Exception):
    pass


class MultiRootException(Exception):
    pass


class DepartmentSerializer(serializers.ModelSerializer):
    parent = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=core_models.Department.objects.all(), required=False, allow_null=True)

    manager = serializers.PrimaryKeyRelatedField(
        read_only=False, queryset=core_models.Employee.objects.all(), required=False, allow_null=True)

    class Meta:
        model = core_models.Department
        fields = [
            'id',
            'name',
            'parent',
            'manager',
        ]

    def create(self, validated_data):
        root = core_models.Department.objects.filter(parent=None).first()
        if ('parent' not in validated_data or validated_data['parent'] is None) and root is not None:
            raise MultiRootException
        else:
            return super(DepartmentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        def Get_Parent(department):
            return department.parent

        instance.name = validated_data['name']
        instance.manager = validated_data['manager']
        instance.parent = validated_data['parent']

        parent = validated_data['parent']
        while parent.parent is not None:
            parent = Get_Parent(parent)
            if parent.id == instance.id:
                raise CycleParentException

        instance.save()
        return instance
