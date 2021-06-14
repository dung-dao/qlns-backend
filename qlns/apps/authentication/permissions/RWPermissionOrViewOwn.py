from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import DjangoModelPermissions, SAFE_METHODS


class RWPermissionOrViewOwn(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.change_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.change_%(model_name)s'],
    }

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_superuser:
            return True
        if obj.owner.user == request.user and request.method in SAFE_METHODS:
            return True
        else:
            return super(RWPermissionOrViewOwn, self).has_object_permission(request, view, obj)

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        employee_pk = view.kwargs['employee_pk']
        try:
            editor_pk = request.user.employee.pk if request.user.employee is not None else None
        except ObjectDoesNotExist:
            return request.user.is_superuser and request.user.is_active

        if employee_pk == str(editor_pk) and request.method in SAFE_METHODS:
            return True
        return super(RWPermissionOrViewOwn, self).has_permission(request, view)
