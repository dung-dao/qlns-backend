from rest_framework import serializers

from qlns.apps.attendance.models import EmployeeFace
from qlns.apps.attendance.services.face_services import add_recognition_image


class EmployeeFaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeFace
        exclude = ()
        read_only_fields = ('azure_face_id', 'owner', 'timestamp',)

    def create(self, validated_data):
        employee = self.context.get('employee', None)
        face_id = self.context.get('face_id', None)

        validated_data['azure_face_id'] = face_id
        validated_data['owner'] = employee

        return super(EmployeeFaceSerializer, self).create(validated_data)
