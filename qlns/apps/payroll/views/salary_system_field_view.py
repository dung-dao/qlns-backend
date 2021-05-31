from rest_framework import permissions, status
from rest_framework import viewsets, mixins
from rest_framework.response import Response

from qlns.apps.payroll.models import SalarySystemField
from qlns.apps.payroll.serializers.salary_system_field_serializer import SalarySystemFieldSerializer


class SalarySystemFieldView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    serializer_class = SalarySystemFieldSerializer
    queryset = SalarySystemField.objects.all()

    def update(self, request, *args, **kwargs):
        if not request.user.has_perm('payroll.change_salarysystemfield'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            return super(SalarySystemFieldView, self).update(request, *args, **kwargs)
