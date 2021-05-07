from datetime import datetime

import pytz
from django.db.models import Q
from django.db.transaction import atomic, set_rollback
from django.shortcuts import get_object_or_404
from django.utils import timezone
from geopy import distance
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from qlns.apps.attendance.models import Attendance, Tracking, TimeOff
from qlns.apps.attendance.serializers.attendance import AttendanceSerializer
from qlns.apps.attendance.serializers.attendance.edit_actual_serializer import EditActualSerializer
from qlns.apps.attendance.serializers.attendance.edit_overtime_serializer import EditOvertimeSerializer
from qlns.apps.core.models import Employee
from qlns.utils.constants import MIN_UTC_DATETIME, MAX_UTC_DATETIME
from qlns.utils.datetime_utils import parse_iso_datetime


class EmployeeAttendanceView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(Q(owner=self.kwargs['employee_pk']))

    def list(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('from_date', None)
        end_date = self.request.query_params.get('to_date', None)

        start_date = parse_iso_datetime(start_date, MIN_UTC_DATETIME)
        end_date = parse_iso_datetime(end_date, MAX_UTC_DATETIME)

        attendance_data = self.get_queryset() \
            .filter(Q(date__gte=start_date) &
                    Q(date__lte=end_date))

        return Response(data=AttendanceSerializer(attendance_data, many=True).data)

    @atomic
    @action(detail=False, methods=['post'])
    def check_in(self, request, employee_pk=None):
        employee = get_object_or_404(Employee, pk=employee_pk)
        schedule = employee.get_current_schedule()

        # Check if employee doesn't have schedule
        if schedule is None:
            return Response(status=status.HTTP_403_FORBIDDEN, data="NO_SCHEDULE")

        today = timezone.now()
        locale_today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

        locale_today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Check if overlapped with an approved time off
        time_off_overlapped = TimeOff.objects.filter(
            Q(owner=employee) &
            Q(start_date__lte=today) &
            Q(end_date__gte=today) &
            Q(status=TimeOff.TimeOffStatus.Approved)
        ).exists()

        if time_off_overlapped:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="OVERLAPPED_WITH_APPROVED_TIME_OFF")

        # Get today attendance
        attendance = Attendance.objects \
            .filter(Q(date__gte=locale_today_start) &
                    Q(date__lte=locale_today_end) &
                    Q(owner=employee_pk) &
                    Q(schedule=schedule)) \
            .first()

        # Check if already check in
        if attendance is not None:
            log = attendance.tracking_data.filter(check_out_time=None).first()
            if log is not None:
                set_rollback(True)
                return Response(status=status.HTTP_400_BAD_REQUEST, data="ALREADY_CHECK_IN")

        else:
            attendance = Attendance(
                owner=employee,
                schedule=schedule,
                date=today,
                status=Attendance.AttendanceLogStatus.Pending
            )

        attendance.save()

        # Get location
        location = employee.get_job_location()
        if location is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="NO_JOB")

        check_in_lat = request.data.get('check_in_lat', None)
        check_in_lng = request.data.get('check_in_lng', None)
        check_in_note = request.data.get('check_in_note', None)

        check_in_outside = None

        if location.enable_geofencing:
            if check_in_lat is None or check_in_lng is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Geo Info required")

            center = (location.lat, location.lng)
            actual_position = (check_in_lat, check_in_lng)

            dis = distance.distance(center, actual_position).m

            check_in_outside = dis > location.radius

            if check_in_outside and check_in_note is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Check in outside require check_in_note")
        else:
            check_in_outside = None

        # Create Tracking
        tracking = Tracking(
            attendance=attendance,

            check_in_time=today,

            check_in_lat=check_in_lat,
            check_in_lng=check_in_lng,
            check_in_outside=check_in_outside,

            check_in_note=request.data.get('check_in_note', None),
            location=location
        )

        tracking.save()
        return Response()

    @atomic()
    @action(detail=False, methods=['post'])
    def check_out(self, request, employee_pk):
        employee = get_object_or_404(Employee, pk=employee_pk)
        schedule = employee.get_current_schedule()

        # Get today attendance
        today = timezone.now()

        locale_today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)

        locale_today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)

        attendance = Attendance.objects \
            .filter(Q(date__gte=locale_today_start) &
                    Q(date__lte=locale_today_end) &
                    Q(owner=employee_pk) &
                    Q(schedule=schedule)) \
            .prefetch_related('tracking_data') \
            .first()

        if attendance is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="NOT_CHECK_IN_YET")

        tracking = attendance.tracking_data.filter(check_out_time=None).first()
        if tracking is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # CHECK OUT OUTSIDE
        check_out_lat = request.data.get('check_out_lat', None)
        check_out_lng = request.data.get('check_out_lng', None)
        check_out_note = request.data.get('check_out_note', tracking.check_out_note)

        check_out_outside = None

        location = employee.get_job_location()
        if location is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="NO_JOB")

        if location.enable_geofencing:
            if check_out_lat is None or check_out_lng is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Geo Info required")

            center = (location.lat, location.lng)
            actual_position = (check_out_lat, check_out_lng)

            dis = distance.distance(center, actual_position).m

            check_out_outside = dis > location.radius

            if check_out_outside and check_out_note is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Check out outside require check_out_note")
        else:
            check_out_outside = None

        # Check Out
        tracking.check_out_time = datetime.utcnow().replace(tzinfo=pytz.utc)
        tracking.check_out_lat = check_out_lat
        tracking.check_out_lng = check_out_lng
        tracking.check_out_note = check_out_note
        tracking.check_out_outside = check_out_outside

        tracking.save()

        tracking.is_overtime = tracking.check_overtime()
        tracking.save()

        # Calculate work hours
        attendance.calculate_work_hours()
        attendance.save()
        return Response()

    @action(detail=True, methods=['post'])
    def revert(self, request, employee_pk, pk):
        employee = get_object_or_404(Employee, pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status == Attendance.AttendanceLogStatus.Pending or \
                attendance.is_confirmed:
            return Response(status=status.HTTP_403_FORBIDDEN)

        attendance.status = Attendance.AttendanceLogStatus.Pending
        attendance.reviewed_by = request.user.employee
        attendance.save()

        return Response()

    @action(detail=True, methods=['post'])
    def reject(self, request, employee_pk, pk):
        employee = get_object_or_404(Employee, pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status != Attendance.AttendanceLogStatus.Pending:
            return Response(status=status.HTTP_403_FORBIDDEN)

        attendance.status = Attendance.AttendanceLogStatus.Rejected
        attendance.reviewed_by = request.user.employee
        attendance.save()

        return Response()

    @action(detail=True, methods=['post'])
    def approve(self, request, employee_pk, pk):
        employee = get_object_or_404(Employee, pk=employee_pk)

        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status != Attendance.AttendanceLogStatus.Pending:
            return Response(status=status.HTTP_403_FORBIDDEN)

        attendance.status = Attendance.AttendanceLogStatus.Approved
        attendance.reviewed_by = request.user.employee

        attendance.save()

        return Response()

    @action(detail=True, methods=['post'])
    def confirm(self, request, employee_pk, pk):
        employee = get_object_or_404(Employee, pk=employee_pk)
        author = request.user.employee

        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.is_confirmed:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif attendance.status == Attendance.AttendanceLogStatus.Pending:
            attendance.status = Attendance.AttendanceLogStatus.Approved
            attendance.reviewed_by = author

            attendance.is_confirmed = True
            attendance.confirmed_by = author

        elif attendance.status == Attendance.AttendanceLogStatus.Approved or \
                attendance.status == Attendance.AttendanceLogStatus.Rejected:
            attendance.is_confirmed = True
            attendance.confirmed_by = author
        else:
            raise Exception("Unreachable code")

        attendance.save()
        return Response()

    @action(detail=True, methods=['post'])
    def edit_actual_hours(self, request, employee_pk, pk):
        employee = get_object_or_404(Employee, pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()

        # Validate
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.is_confirmed:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Cannot edit confirmed attendance")

        serializer = EditActualSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        attendance.actual_work_hours = serializer.validated_data.get('actual_work_hours')
        attendance.actual_hours_modified = True
        attendance.actual_hours_modification_note = serializer.validated_data.get('actual_hours_modification_note')

        attendance.save()

        return Response(data=AttendanceSerializer(attendance).data)

    @action(detail=True, methods=['post'])
    def edit_overtime_hours(self, request, employee_pk, pk):
        employee = get_object_or_404(Employee, pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()

        # Validate
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.is_confirmed:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Cannot edit confirmed attendance")

        serializer = EditOvertimeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        attendance.ot_work_hours = serializer.validated_data.get('ot_work_hours')
        attendance.ot_hours_modified = True
        attendance.ot_hours_modification_note = serializer.validated_data.get('ot_hours_modification_note')

        attendance.save()

        return Response(data=AttendanceSerializer(attendance).data)
