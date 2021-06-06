from django.contrib.auth.models import Group, Permission, User
from django.db.transaction import atomic
from rest_framework import serializers


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename']


class PermissionStatusSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    codename = serializers.CharField()
    has_perm = serializers.BooleanField()

    def update(self, instance, validated_data):
        raise Exception('Cannot use PermissionStatusSerializer for updating data')

    def create(self, validated_data):
        raise Exception('Cannot use PermissionStatusSerializer for creating object')


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionStatusSerializer(many=True)

    all_perm_str_query = "SELECT DISTINCT perm.* FROM auth_permission perm LEFT JOIN qlns.django_content_type " \
                         "ctt ON perm.content_type_id = ctt.id WHERE NOT ctt.app_label='admin' AND NOT " \
                         "ctt.app_label='sessions' AND NOT ctt.app_label='contenttypes' AND NOT " \
                         "ctt.app_label='django_q' ORDER BY perm.id "

    def get_all_perms(self):
        return Permission.objects.raw(self.all_perm_str_query)

    def to_representation(self, instance):
        all_permissions = list(self.get_all_perms())
        permissions = list(instance.permissions.all())

        def map_permission_to_perm_status(perm):
            return {'id': perm.id,
                    'name': perm.name,
                    'codename': perm.codename,
                    'has_perm': perm in permissions}

        permission_statuses = list(map(map_permission_to_perm_status, all_permissions))
        return {
            'id': instance.id,
            'name': instance.name,
            'permissions': permission_statuses
        }

    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

    @atomic
    def create(self, validated_data):
        newgroup = Group(name=validated_data['name'])
        newgroup.save()

        all_perms = self.get_all_perms()
        permission_data = validated_data.pop('permissions')
        enable_perms = list(filter(lambda e: e['has_perm'], permission_data))
        permission_code_pks = list(map(lambda e: e['id'], enable_perms))
        permissions = list(filter(lambda perm: perm.id in permission_code_pks, all_perms))

        if len(permissions) > 0:
            newgroup.permissions.set(permissions)
            newgroup.save()
        return newgroup

    def update(self, instance, validated_data):
        if instance.name is not None:
            instance.name = validated_data.get('name', instance)

        all_perms = self.get_all_perms()
        permission_data = validated_data.pop('permissions')
        enable_perms = list(filter(lambda e: e['has_perm'], permission_data))
        permission_code_pks = list(map(lambda e: e['id'], enable_perms))
        permissions = list(filter(lambda perm: perm.id in permission_code_pks, all_perms))

        if len(permissions) > 0:
            instance.permissions.set(permissions)

        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'is_staff', 'date_joined', 'is_active']
        read_only_fields = ['date_joined', 'id', 'is_active', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data['username']
        is_staff = validated_data['is_staff']
        password = validated_data['password']

        user = User(username=username, is_staff=is_staff, is_superuser=False)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            instance.username = validated_data.get(
                'username', instance.username)

        if 'password' in validated_data:
            instance.set_password(validated_data['validated_data'])

        if 'is_staff' in validated_data:
            instance.is_staff = validated_data.get(
                'is_staff', instance.is_staff)

        return instance


class ProfileUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'is_staff', 'date_joined']
        read_only_fields = ['date_joined', 'id', 'is_staff']
