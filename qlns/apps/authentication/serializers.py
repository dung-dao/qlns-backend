from rest_framework import serializers
from django.contrib.auth.models import Group, Permission, User
from .models import Employee, Country


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
                  'last_name', 'date_joined', 'is_staff', 'is_superuser']
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


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)
    supervisor = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), allow_null=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), allow_null=True)

    class Meta:
        model = Employee
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            is_staff=user_data['is_staff'],
            is_superuser=user_data['is_superuser'],
        )

        user.set_password(user_data['password'])

        user.save()

        employee = Employee(**validated_data)
        employee.user = user

        employee.save()
        return employee

    def update(self, instance, validated_data):
        user = None
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            for key in user_data:
                if key != "password":
                    setattr(user, key, user_data[key])
                else:
                    user.set_password(user_data['password'])
            user.save()

        for key in validated_data:
            setattr(instance, key, validated_data[key])

        instance.save()
        return instance
