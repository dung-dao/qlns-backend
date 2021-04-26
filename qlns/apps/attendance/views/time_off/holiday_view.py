from rest_framework import viewsets, mixins

from qlns.apps.attendance.models import Holiday
from qlns.apps.attendance.serializers import HolidaySerializer


class HolidayView(
    viewsets.GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin
):
    serializer_class = HolidaySerializer
    queryset = Holiday.objects.all()

    def get_queryset(self):
        query_params = self.request.query_params

        return self.queryset.filter(
            start_date__gte=query_params.get('from_date', '1970-1-1'),
            start_date__lte=query_params.get('to_date', '2999-1-1'),
        )
