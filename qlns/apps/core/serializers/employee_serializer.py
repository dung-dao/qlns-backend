from rest_framework import serializers
from qlns.apps.authentication.serializers import UserSerializer
from qlns.apps.core.models import Employee, Country
from django.contrib.auth.models import User


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=False)
    nationality = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Country.objects.all(),
        allow_null=True, required=False)
    role = serializers.CharField(source="get_role", read_only=True)
    status = serializers.CharField(source="get_status", read_only=True)

    class Meta:
        model = Employee
        exclude = ('current_job',)

    def create(self, validated_data):
        # Create user
        user_data = validated_data.pop('user')
        user = User(
            username=user_data['username'],
            is_superuser=False,
        )

        user.set_password(user_data['password'])
        user.save()

        # Create employee
        employee = Employee(**validated_data)

        # Associate
        employee.user = user

        employee.save()
        return employee

    def update(self, instance, validated_data):
        # Update user
        user = None
        if 'user' in validated_data:
            user_data = validated_data.pop('user')
            user = instance.user
            for key in user_data:
                if key == 'id':
                    continue
                if key != "password":
                    setattr(user, key, user_data[key])
                else:
                    user.set_password(user_data['password'])
            user.save()

        super(EmployeeSerializer, self).update(instance, validated_data)

        instance.save()
        return instance
