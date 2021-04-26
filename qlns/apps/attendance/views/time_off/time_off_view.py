from datetime import MAXYEAR

from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from qlns.apps.attendance.models import TimeOff
from qlns.apps.core.models import Employee


class TimeOffEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ('id', 'first_name', 'last_name', 'avatar',)


class TimeOffListItemSerializer(serializers.ModelSerializer):
    owner = TimeOffEmployeeSerializer(read_only=True)
    time_off_type = serializers.SlugRelatedField("name", read_only=True)

    class Meta:
        model = TimeOff
        fields = ('id', 'owner', 'reviewed_by',
                  'time_off_type', 'start_date', 'end_date',
                  'status', 'note',)


class TimeOffView(APIView):
    def get(self, request):
        params = self.request.query_params
        start_date = params.get('start_date', '1970-1-1')
        end_date = params.get('end_date', f'{MAXYEAR}-12-31')

        instances = TimeOff.objects.filter(
            start_date__gte=start_date,
            start_date__lte=end_date
        ).select_related('owner', 'reviewed_by', 'time_off_type')

        serializer = TimeOffListItemSerializer(instance=instances, many=True, context={"request": request})
        return Response(data=serializer.data)
