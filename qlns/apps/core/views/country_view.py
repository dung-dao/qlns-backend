from django.db.models import ProtectedError
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

from qlns.apps.core.models import Country
from qlns.apps.core.serializers import CountrySerializer


class CountryView(viewsets.ModelViewSet):
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly,)
    queryset = Country.objects.all()
    serializer_class = CountrySerializer

    def destroy(self, request, *args, **kwargs):
        try:
            return super(CountryView, self).destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"Delete referenced record not allowed"}
            )
