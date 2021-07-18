from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.attendance.services.face_services import create_person, add_recognition_image
from qlns.apps.authentication.permissions import CRUDPermission
from qlns.apps.core.models import Employee, ApplicationConfig
from qlns.apps.core.serializers import EmployeeSerializer


class EmployeeView(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_permissions(self):
        permission_classes = (permissions.IsAuthenticated,)
        if self.action in ['list', 'create', 'update', ]:
            permission_classes = (CRUDPermission,)

        return [permission() for permission in permission_classes]

    def get_action_perm(self):
        app_label = self.serializer_class.Meta.model._meta.app_label
        model = self.serializer_class.Meta.model._meta.model_name
        perm = f'{app_label}.can_{self.action}_{model}'.lower()
        return perm

    un_authorized = {
        "detail": "You do not have permission to perform this action."
    }

    def get_employee_pk(self):
        try:
            return str(self.request.user.employee.pk)
        except ObjectDoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        pk = self.get_pk(kwargs)
        employee_pk = self.get_employee_pk()

        if employee_pk != pk and \
                not request.user.has_perm('core.view_employee'):
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)
        return super(EmployeeView, self).retrieve(request, *args, **kwargs)

    def get_pk(self, kwargs):
        return kwargs.get('pk', None)

    def partial_update(self, request, *args, **kwargs):
        pk = self.get_pk(kwargs)
        employee_pk = self.get_employee_pk()

        if employee_pk != pk and \
                not request.user.has_perm('core.change_employee'):
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)
        return super(EmployeeView, self).partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        pk = self.get_pk(kwargs)
        employee_pk = self.get_employee_pk()

        if employee_pk != pk and \
                not request.user.has_perm('core.change_employee'):
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)
        return super(EmployeeView, self).update(request, *args, **kwargs)

    @action(methods=['post'], detail=True, url_path='role')
    def set_role(self, request, pk=None):
        # Authorize
        perm = self.get_action_perm()
        if not request.user.has_perm(perm):
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)

        employee = get_object_or_404(Employee, pk=pk)
        group = get_object_or_404(Group, name=request.data['name'])
        employee.user.groups.set([group])
        employee.user.save()
        return Response()

    @action(methods=['put'], detail=True, url_path='password')
    def set_password(self, request, pk):
        # Authorize
        perm = self.get_action_perm()
        if not request.user.has_perm(perm) and \
                not str(request.user.employee.pk) == pk:
            return Response(status=status.HTTP_403_FORBIDDEN, data=self.un_authorized)

        if 'new_password' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        employee = get_object_or_404(Employee, pk=pk)
        new_password = request.data['new_password']
        employee.user.set_password(new_password)
        employee.user.save()
        return Response()

    @atomic
    @action(methods=['post'], detail=True, url_path='avatar')
    def change_avatar(self, request, pk):
        if 'avatar' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            if self.request.user.employee.pk != int(pk):
                return Response(status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        employee = get_object_or_404(Employee, pk=pk)
        employee.avatar = request.data['avatar']
        employee.save()
        return Response()
