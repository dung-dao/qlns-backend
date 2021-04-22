from datetime import date, datetime

from django.db.transaction import atomic, set_rollback
from django.shortcuts import get_object_or_404
from geopy import distance
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from qlns.apps.attendance.models import Attendance, Tracking, OvertimeType
from qlns.apps.attendance.serializers.attendance import AttendanceSerializer
from qlns.apps.attendance.serializers.attendance.edit_actual_serializer import EditActualSerializer
from qlns.apps.attendance.serializers.attendance.edit_overtime_serializer import EditOvertimeSerializer
from qlns.apps.core.models import Employee


class EmployeeAttendanceView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(owner=self.kwargs['employee_pk'])

    # employee
    @action(detail=False, methods=['post'])
    @atomic()
    def check_in(self, request, employee_pk=None):
        employee = Employee.objects.get(pk=employee_pk)
        schedule = employee.get_current_schedule()

        # NO SCHEDULE EXCEPTION
        if schedule is None:
            return Response(status=status.HTTP_403_FORBIDDEN, data="NO_SCHEDULE")

        today = date.today()

        # Get today attendance
        attendance = Attendance.objects.filter(
            date__year=today.year,
            date__month=today.month,
            date__day=today.day,

            owner=employee_pk,
            schedule=schedule
        ).first()

        # ALREADY_CHECK_IN_EXCEPTION
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

        # SAVE ATTENDANCE
        attendance.save()

        # Get OvertimeType
        # overtime_type = get_object_or_404(OvertimeType, name=request.data['overtime_type'])
        overtime_type = None
        overtime_type_name = request.data.get('overtime_type', None)

        if overtime_type_name is None:
            overtime_type = None
        else:
            overtime_type = get_object_or_404(OvertimeType, name=overtime_type_name)

        # TODO: Check valid OT (not in schedule)

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

        # Create Tracking info
        tracking = Tracking(
            attendance=attendance,
            overtime_type=overtime_type,

            check_in_time=datetime.utcnow(),

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

        # Get attendance
        today = date.today()
        attendance = Attendance.objects.filter(
            date__year=today.year,
            date__month=today.month,
            date__day=today.day,

            owner=employee_pk
        ).first()

        # TODO: refactor this later
        if attendance is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="NOT_CHECK_IN_YET")

        tracking = attendance.tracking_data.filter(check_out_time=None).first()
        if tracking is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # TODO: CHECK OUT OUTSIDE
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
        tracking.check_out_time = datetime.utcnow()
        tracking.check_out_lat = check_out_lat
        tracking.check_out_lng = check_out_lng
        tracking.check_out_note = check_out_note
        tracking.check_out_outside = check_out_outside

        tracking.save()

        # Calculate work hours
        attendance.calculate_work_hours()
        attendance.save()
        return Response()

    @action(detail=True, methods=['post'])
    def revert(self, request, employee_pk, pk):
        employee = Employee.objects.get(pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status == Attendance.AttendanceLogStatus.Pending or \
                attendance.status == Attendance.AttendanceLogStatus.Confirmed:
            return Response(status=status.HTTP_403_FORBIDDEN)

        attendance.status = Attendance.AttendanceLogStatus.Pending
        attendance.reviewed_by = request.user

        return Response()

    @action(detail=True, methods=['post'])
    def reject(self, request, employee_pk, pk):
        employee = Employee.objects.get(pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status != Attendance.AttendanceLogStatus.Pending:
            return Response(status=status.HTTP_403_FORBIDDEN)

        attendance.status = Attendance.AttendanceLogStatus.Rejected
        attendance.reviewed_by = request.user

        return Response()

    @action(detail=True, methods=['post'])
    def approve(self, request, employee_pk, pk):
        # Đặt status thành approved, tạm chấp nhận kết quả nhưng chưa sử dụng để tính lương
        employee = Employee.objects.get(pk=employee_pk)
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
        # Chỉnh sửa lại actual hour nếu có khiếu nại, confirm để đặt status là confirm.
        # Dữ liệu này sẽ được sử dụng để tinh lương.

        employee = Employee.objects.get(pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status == Attendance.AttendanceLogStatus.Pending:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="Approve or reject first")

        attendance.status = Attendance.AttendanceLogStatus.Confirmed
        attendance.confirmed_by = request.user.employee

        attendance.save()

        return Response()

    @action(detail=True, methods=['post'])
    def edit_actual_hours(self, request, employee_pk, pk):
        employee = Employee.objects.get(pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()

        # Validate
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status == Attendance.AttendanceLogStatus.Confirmed:
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
        employee = Employee.objects.get(pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()

        # Validate
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status == Attendance.AttendanceLogStatus.Confirmed:
            return Response(status=status.HTTP_403_FORBIDDEN, data="Cannot edit confirmed attendance")

        serializer = EditOvertimeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        attendance.ot_work_hours = serializer.validated_data.get('ot_work_hours')
        attendance.ot_hours_modified = True
        attendance.ot_hours_modification_note = serializer.validated_data.get('ot_hours_modification_note')

        attendance.save()

        return Response(data=AttendanceSerializer(attendance).data)
