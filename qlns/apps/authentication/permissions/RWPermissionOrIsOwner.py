from qlns.apps.authentication.permissions import DjangoModelPermissionOrIsOwner


class RWPermissionOrIsOwner(DjangoModelPermissionOrIsOwner):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': [],
        'HEAD': [],
        'POST': ['%(app_label)s.change_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.change_%(model_name)s'],
    }
