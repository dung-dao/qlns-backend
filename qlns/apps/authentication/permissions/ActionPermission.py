from rest_framework import permissions


class ActionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action in ('list', 'retrieve', 'create', 'update', 'partial_update', 'destroy',):
            raise Exception('unreachable code')
        if not (request.user and request.user.is_authenticated):
            return False
        app_label = view.serializer_class.Meta.model._meta.app_label
        model = view.serializer_class.Meta.model._meta.model_name
        perm = f'{app_label}.can_{view.action}_{model}'.lower()
        return request.user.has_perm(perm)
