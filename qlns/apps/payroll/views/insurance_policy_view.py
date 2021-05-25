from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from qlns.apps.payroll.models import InsurancePolicy
from qlns.apps.payroll.serializers import InsurancePolicySerializer


class InsurancePolicyView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    serializer_class = InsurancePolicySerializer
    queryset = InsurancePolicy.objects.all()
