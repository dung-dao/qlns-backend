from django.db.models import Q
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.response import Response

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

    def create(self, request, *args, **kwargs):
        serializer = HolidaySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        # Check overlapped
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        overlapped = self.get_queryset().filter(
            Q(start_date__gte=start_date) & Q(start_date__lte=end_date) |
            Q(end_date__gte=start_date) & Q(end_date__lte=end_date)
        ).exists()

        if overlapped:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data="overlapped with another holiday".upper().strip().replace(' ', '_'))

        serializer.save()
        return Response(data=serializer.data)
