from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly
from rest_framework.response import Response

from qlns.apps.payroll.models import InsurancePolicy
from qlns.apps.payroll.serializers import InsurancePolicySerializer


class InsurancePolicyView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = InsurancePolicySerializer
    queryset = InsurancePolicy.objects.all()

    def destroy(self, request, *args, **kwargs):
        try:
            return super(InsurancePolicyView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Delete referenced record not allowed"}
            )
