from rest_framework import serializers
from hrm_api.serializers import GroupSerializer
from django.contrib.auth.models import Group
from hrm_api.models import Staff
from django.core.exceptions import ObjectDoesNotExist


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'email', 'username', 'password',
                  'first_name', 'last_name', 'date_joined',
                  'phone', 'facebook', 'linkedin', 'skype',
                  'is_staff', 'is_superuser', 'role']
        read_only_fields = ['date_joined', 'id']
        extra_kwargs = {'password': {'write_only': True}}

    role = serializers.CharField(source="get_role")

    def create(self, validated_data):
        new_staff = Staff(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone=validated_data['phone'],
            facebook=validated_data['facebook'],
            linkedin=validated_data['linkedin'],
            skype=validated_data['skype'],
            is_staff=validated_data['is_staff'],
            is_superuser=validated_data['is_superuser'],
        )

        # Change password
        new_staff.set_password(validated_data['password'])

        # Set Role
        if validated_data['get_role'] is not None:
            rolename = validated_data['get_role']
            if rolename.upper() == "ADMIN":
                new_staff.is_superuser = True
                new_staff.groups.clear()
            else:
                new_staff.is_superuser = False
                roles = []
                roles.append(Group.objects.get(name__iexact=rolename))
                new_staff.groups.set(roles)

        new_staff.save()
        return new_staff

    def update(self, instance, validated_data):
        for key in validated_data:
            if key == "password":
                instance.set_password(validated_data['password'])
            elif key == "get_role":
                rolename = validated_data['get_role']
                if rolename.upper() == "ADMIN":
                    instance.is_superuser = True
                    instance.groups.clear()
                else:
                    instance.is_superuser = False
                    roles = []
                    roles.append(Group.objects.get(name__iexact=rolename))
                    instance.groups.set(roles)
            elif key == "id":
                continue
            else:
                setattr(instance, key, validated_data[key])

        instance.save()
        return instance
