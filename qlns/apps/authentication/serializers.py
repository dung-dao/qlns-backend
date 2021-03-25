from rest_framework import serializers
from django.contrib.auth.models import Group, Permission, User


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True)

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'first_name',
                  'last_name', 'date_joined', 'is_staff']
        read_only_fields = ['date_joined', 'id']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data['username']
        is_staff = validated_data['is_staff']
        is_superuser = validated_data['is_superuser']
        password = validated_data['password']

        user = User(username=username, is_staff=is_staff,
                    is_superuser=is_superuser)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            instance.username = validated_data.get(
                'username', instance.username)

        if 'password' in validated_data:
            instance.username = validated_data.get(
                'username', instance.username)

        if 'is_staff' in validated_data:
            instance.username = validated_data.get(
                'username', instance.username)

        if 'is_superuser' in validated_data:
            instance.username = validated_data.get(
                'username', instance.username)
