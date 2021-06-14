from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from qlns.apps.payroll.models import TaxPolicy
from qlns.apps.payroll.serializers import TaxPolicySerializer


class TaxPolicyView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = TaxPolicy.objects.all()
    serializer_class = TaxPolicySerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super(TaxPolicyView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Delete referenced record not allowed"}
            )
