from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

from qlns.apps.payroll.models import TaxPolicy
from qlns.apps.payroll.serializers import TaxPolicySerializer


class TaxPolicyView(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)
    queryset = TaxPolicy.objects.all()
    serializer_class = TaxPolicySerializer
