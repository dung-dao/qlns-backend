from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from qlns.apps.core.models import Employee
from qlns.apps.core.serializers import EmployeeSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import Group
from rest_framework import permissions
from rest_framework import status


class EmployeeView(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Insert permission here
            permission_classes = ()
        elif self.action == 'create':
            permission_classes = ()
        elif self.action == 'set_password':
            permission_classes = (permissions.IsAuthenticated,)
        else:
            permission_classes = ()
        return [permission() for permission in permission_classes]

    @action(methods=['post'], detail=True, url_path='role', permission_classes=())
    def set_role(self, request, pk=None):
        employee = get_object_or_404(Employee, pk=pk)
        group = get_object_or_404(Group, name=request.data['name'])
        employee.user.groups.set([group])
        employee.user.save()
        return Response()

    @action(methods=['put'], detail=True, url_path='password')
    def set_password(self, request, pk):
        if 'new_password' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        employee = get_object_or_404(Employee, pk=pk)
        new_password = request.data['new_password']
        employee.user.set_password(new_password)
        employee.user.save()
        return Response()

    @action(methods=['put'], detail=True, url_path='avatar')
    def change_avatar(self, request, pk):
        if 'avatar' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        employee = get_object_or_404(Employee, pk=pk)
        employee.avatar = request.data['avatar']
        employee.save()
        return Response()
