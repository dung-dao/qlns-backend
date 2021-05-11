from rest_framework import viewsets, mixins

from qlns.apps.attendance.models import Period
from qlns.apps.attendance.serializers import PeriodSerializer


class PeriodView(viewsets.GenericViewSet,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
