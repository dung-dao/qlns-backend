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
from qlns.apps.core.models import Employee


class EmployeeAttendanceView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = (IsAuthenticated,)

    # employee
    @action(detail=False, methods=['post'])
    @atomic()
    def check_in(self, request, employee_pk=None):
        # TODO: Validate
        # Employee info
        employee = Employee.objects.get(pk=employee_pk)

        schedule = employee.get_current_schedule()

        today = date.today()

        # Get today's attendance
        attendance = Attendance.objects.filter(
            date__year=today.year,
            date__month=today.month,
            date__day=today.day,

            owner=employee_pk,
            schedule=schedule
        ).first()

        # TODO: Check if there is a tracking which is not checked out => BAD REQUEST
        if attendance is not None:
            log = attendance.tracking_data.filter(check_out_time=None).first()
            if log is not None:
                set_rollback(True)
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Checkout first")

        # Tạo attendance mới nếu chưa có
        if attendance is None:
            attendance = Attendance(
                owner=employee,
                schedule=schedule,
                date=today,
                status=Attendance.AttendanceLogStatus.Pending
            )

        attendance.save()

        # Get OvertimeType
        overtime_type = get_object_or_404(OvertimeType, name=request.data['overtime_type'])

        # Handle location
        # TODO: CHECK IF ALLOW OUTSIDE
        location = employee.get_job_location()

        check_in_outside = False
        check_in_lat = request.data.get('check_in_lat', None)
        check_in_lng = request.data.get('check_in_lng', None)

        if not location.allow_outside:
            center = (location.lat, location.lng)

            if (check_in_lat is None) or (check_in_lng is None):
                set_rollback(True)
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Location required")

            actual_position = (check_in_lat, check_in_lng)
            dis = distance.distance(center, actual_position).m
            if dis > location.radius:
                set_rollback(True)
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Outside working zone")

        # TODO: Check invalid OT

        # Create Tracking
        # Tạo Tracking mới, nhập thông tin checkin
        tracking = Tracking(
            attendance=attendance,
            overtime_type=overtime_type,

            check_in_time=datetime.utcnow(),

            check_in_lat=check_in_lat,
            check_in_lng=check_in_lng,
            check_in_outside=check_in_outside,

            check_in_note=request.data.get('check_in_note', None),
        )

        tracking.save()
        return Response()

    @atomic()
    @action(detail=False, methods=['post'])
    def check_out(self, request, employee_pk):
        # Nhập thông tin checkout
        employee = Employee.objects.get(pk=employee_pk)

        # Get attendance
        today = date.today()
        attendance = Attendance.objects.filter(
            date__year=today.year,
            date__month=today.month,
            date__day=today.day,

            owner=employee_pk
        ).first()
        if attendance is None:
            set_rollback(True)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tracking = attendance.tracking_data.filter(check_out_time=None).first()
        if tracking is None:
            set_rollback(True)
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # TODO: CHECK OUTSIDE
        check_out_outside = False

        location = employee.get_job_location()

        check_out_lat = request.data.get('check_out_lat', None)
        check_out_lng = request.data.get('check_out_lng', None)

        if not location.allow_outside:
            center = (location.lat, location.lng)

            if (check_out_lat is None) or (check_out_lng is None):
                set_rollback(True)
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Location required")

            actual_position = (check_out_lat, check_out_lng)
            dis = distance.distance(center, actual_position).m
            if dis > location.radius:
                set_rollback(True)
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Outside working zone")

        # Checkout
        tracking.check_out_time = datetime.utcnow()
        tracking.check_out_lat = check_out_lat
        tracking.check_out_lng = check_out_lng
        tracking.check_out_outside = check_out_outside
        tracking.check_out_note = request.data.get('check_out_note', tracking.check_out_note)
        tracking.save()
        # Hệ thống sẽ tự checkout mỗi khi hết ca làm việc, nếu sau đó checkin thì phải yêu cầu OT

        tracking_data = attendance.tracking_data.all()
        # Tính toán lại actual work, OT hour của attendance
        attendance.calculate_work_hours()
        attendance.save()
        return Response()

    @action(detail=True)
    def reject(self, request, employee_pk, pk):
        employee = Employee.objects.get(pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

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

        attendance.status = Attendance.AttendanceLogStatus.Confirmed
        attendance.confirmed_by = request.user.employee

        attendance.save()

        return Response()
