from rest_framework.serializers import ModelSerializer
from hrm_api.models import Department, Staff


class DepartmentSerializer(ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'department_name']
