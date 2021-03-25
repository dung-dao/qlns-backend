from rest_framework import viewsets
from rest_framework import permissions
from qlns.apps.core.models import Employee
from qlns.apps.core.serializers import EmployeeSerializer
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.core import exceptions
from rest_framework.decorators import action

from django.contrib.auth.models import Group


class EmployeeView(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissions,)
    queryset = Employee.objects.filter(user__is_active=True)
    serializer_class = EmployeeSerializer

    def destroy(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        user = employee.user
        user.is_active = False
        user.save()
        return Response()

    def partial_update(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        serializer = EmployeeSerializer(
            instance=employee, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

    @action(methods=['post'], detail=True, url_path='role')
    def set_role(self, request, pk=None):
        try:
            employee = Employee.objects.get(pk=pk)

            group = None
            if request.data['name'] == "ADMIN":
                employee.user.is_superuser = True
            else:
                employee.user.is_superuser = False
                groups = [Group.objects.get(pk=request.data['id'])]
                employee.user.groups.set(groups)

            employee.user.save()
            return Response()

        except exceptions.ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data="Role doesn't exist")
