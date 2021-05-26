from rest_framework import viewsets, status
from rest_framework.response import Response

from qlns.apps.authentication.permissions import DjangoModelPermissionOrIsOwner
from qlns.apps.core.models import Dependent
from qlns.apps.core.serializers.dependent_serializer import DependentSerializer


class DependentView(viewsets.ModelViewSet):
    queryset = Dependent.objects.all()
    serializer_class = DependentSerializer
    permission_classes = (DjangoModelPermissionOrIsOwner,)

    def get_queryset(self):
        return self.queryset.filter(owner=self.kwargs.get('employee_pk'))

    def create(self, request, *args, **kwargs):
        employee_id = self.kwargs['employee_pk']
        if 'owner' not in request.data or employee_id != str(request.data['owner']):
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Invalid owner")

        return super(DependentView, self).create(request, *args, **kwargs)
