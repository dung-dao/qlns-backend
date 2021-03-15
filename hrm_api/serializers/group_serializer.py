from rest_framework.serializers import ModelSerializer, ManyRelatedField
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ObjectDoesNotExist


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class GroupSerializer(ModelSerializer):
    permissions = PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def create(self, validated_data):
        newgroup = Group(name=validated_data['name'])
        newgroup.save()

        permission_data = validated_data.pop('permissions')
        permissions = []
        try:
            for per in permission_data:
                permission = Permission.objects.get(**per)
                permissions.append(permission)
        except ObjectDoesNotExist:
            return newgroup

        newgroup.permissions.set(permissions)
        return newgroup

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance)
        permission_data = validated_data.pop('permissions')

        permissions = []
        try:
            for per in permission_data:
                permission = Permission.objects.get(**per)
                permissions.append(permission)
        except ObjectDoesNotExist:
            return instance

        instance.permissions.set(permissions)
        instance.save()
        return instance
