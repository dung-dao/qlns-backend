from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qlns.apps.payroll.models import TaxPolicy
from qlns.apps.payroll.serializers import TaxPolicySerializer


class TaxPolicyView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    queryset = TaxPolicy.objects.all()
    serializer_class = TaxPolicySerializer
