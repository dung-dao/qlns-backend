from rest_framework import serializers
from qlns.apps.authentication.serializers import UserSerializer
from qlns.apps.core.models import Employee, Country
from django.contrib.auth.models import User


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)
    supervisor = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), allow_null=True)
    country = serializers.PrimaryKeyRelatedField(
        queryset=Country.objects.all(), allow_null=True)
    role = serializers.CharField(source="get_role", read_only=True)

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
