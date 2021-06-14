from rest_framework import serializers

from qlns.apps.authentication.serializers import ProfileUserSerializer
from qlns.apps.core.models import Employee, Country


class CurrentUserSerializer(serializers.ModelSerializer):
    user = ProfileUserSerializer(read_only=True)
    nationality = serializers.SlugRelatedField(
        slug_field='name',
        queryset=Country.objects.all(),
        allow_null=True, required=False)
    role = serializers.CharField(source="get_role", read_only=True)

    class Meta:
        model = Employee
        exclude = ('face_model_path', 'current_job',)

    def create(self, validated_data):
        raise Exception('Create profile not allowed')

    def update(self, instance, validated_data):
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

        super(CurrentUserSerializer, self).update(instance, validated_data)

        instance.save()
        return instance
