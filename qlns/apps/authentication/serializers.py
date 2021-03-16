from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import Group, Permission
import qlns.apps.authentication.serializers as m_serializers


class PermissionSerializer(ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class GroupSerializer(ModelSerializer):
    permissions = m_serializers.PermissionSerializer(many=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    def create(self, validated_data):
        newgroup = Group(name=validated_data['name'])
        newgroup.save()

        permission_data = validated_data.pop('permissions')
        permissions = []
        for per in permission_data:
            try:
                permission = Permission.objects.get(**per)
                permissions.append(permission)
            except ObjectDoesNotExist:
                continue
        if len(permissions) > 0:
            newgroup.permissions.set(permissions)
            newgroup.save()
        return newgroup

    def update(self, instance, validated_data):
        if instance.name is not None:
            instance.name = validated_data.get('name', instance)

        permission_data = validated_data.pop('permissions')

        permissions = []
        for per in permission_data:
            try:
                permission = Permission.objects.get(**per)
                permissions.append(permission)
            except ObjectDoesNotExist:
                continue
        if len(permissions) > 0:
            instance.permissions.set(permissions)

        instance.save()
        return instance
