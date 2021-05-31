from rest_framework import viewsets
from rest_framework import permissions
from qlns.apps.core.models import Country
from qlns.apps.core.serializers import CountrySerializer


class CountryView(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
