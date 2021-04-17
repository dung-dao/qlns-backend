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

    # Readonly fields
    employee_no = serializers.IntegerField(source='get_employee_no', read_only=True)
    manager_full_name = serializers.CharField(source="get_manager_full_name", read_only=True)
    manager_avatar = serializers.ImageField(source='get_manager_avatar', read_only=True)

    class Meta:
        model = core_models.Department
        fields = [
            'id',
            'name',
            'parent',
            'manager',
            'description',
            'employee_no',
            'manager_full_name',
            'manager_avatar',
        ]

    def create(self, validated_data):
        root = core_models.Department.objects.filter(parent=None).first()
        if ('parent' not in validated_data or validated_data['parent'] is None) and root is not None:
            raise MultiRootException
        else:
            return super(DepartmentSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        def get_parent(department):
            return department.parent

        if 'name' in validated_data:
            instance.name = validated_data['name']
        if 'manager' in validated_data:
            instance.manager = validated_data['manager']
        if 'parent' in validated_data:
            instance.parent = validated_data['parent']
        if 'description' in validated_data:
            instance.description = validated_data['description']

        parent = validated_data['parent']
        while parent is not None and parent.parent is not None:
            parent = get_parent(parent)
            if parent.id == instance.id:
                raise CycleParentException

        instance.save()
        return instance
