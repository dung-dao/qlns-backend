from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from qlns.apps.payroll.models import InsurancePolicy
from qlns.apps.payroll.serializers import InsurancePolicySerializer


class InsurancePolicyView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = InsurancePolicySerializer
    queryset = InsurancePolicy.objects.all()
