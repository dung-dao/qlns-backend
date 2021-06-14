from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions


class DjangoModelPermissionOrIsOwner(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if obj.owner.user == request.user:
            return True
        else:
            return super(DjangoModelPermissionOrIsOwner, self).has_object_permission(request, view, obj)

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_superuser:
            return True

        employee_pk = view.kwargs['employee_pk']
        try:
            editor_pk = request.user.employee.pk if request.user.employee is not None else None
        except ObjectDoesNotExist:
            return False

        if employee_pk == str(editor_pk):
            return True
        else:
            has_perm = super(DjangoModelPermissionOrIsOwner, self).has_permission(request, view)
            return has_perm
