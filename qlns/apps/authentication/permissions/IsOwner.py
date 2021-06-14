from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False

        if request.user.is_superuser:
            return True

        employee_pk = view.kwargs['employee_pk']
        editor_pk = request.user.employee.pk if request.user.employee is not None else None
        return employee_pk == str(editor_pk)

    def has_object_permission(self, request, view, obj):
        if not (request.user and request.user.is_authenticated):
            return False
        return obj.owner.user == request.user
