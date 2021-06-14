import PIL
from PIL import Image
from django.db.models import Q
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from geopy import distance
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from rest_framework.response import Response

from qlns.apps.attendance.models import Attendance, Tracking, TimeOff, Period
from qlns.apps.attendance.serializers.attendance import AttendanceSerializer
from qlns.apps.attendance.serializers.attendance.check_in_serializer import CheckInDataSerializer
from qlns.apps.attendance.serializers.attendance.check_out_serializer import CheckOutDataSerializer
from qlns.apps.attendance.serializers.attendance.edit_actual_serializer import EditActualSerializer
from qlns.apps.attendance.serializers.attendance.edit_overtime_serializer import EditOvertimeSerializer
from qlns.apps.authentication.permissions import DjangoModelPermissionOrIsOwner, ActionPermission, IsOwner
from qlns.apps.core.models import Employee, ApplicationConfig
from qlns.utils.constants import MIN_UTC_DATETIME, MAX_UTC_DATETIME
from qlns.utils.datetime_utils import parse_iso_datetime, local_now


class EmployeeAttendanceView(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_permissions(self):
        permission_classes = (permissions.IsAuthenticated,)
        if self.action in ['list', ]:
            permission_classes = (DjangoModelPermissionOrIsOwner,)
        elif self.action in ['check_in', 'check_out', ]:
            permission_classes = (IsOwner,)
        elif self.action in ['revert', 'reject', 'approve', 'confirm',
                             'edit_actual_hours', 'edit_overtime_hours']:
            permission_classes = (ActionPermission,)
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.queryset.filter(Q(owner=self.kwargs['employee_pk']))

    def list(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('from_date', None)
        end_date = self.request.query_params.get('to_date', None)
        period_id = self.request.query_params.get('period_id', None)

        start_date = parse_iso_datetime(start_date, MIN_UTC_DATETIME)
        end_date = parse_iso_datetime(end_date, MAX_UTC_DATETIME)

        attendance_data = self.get_queryset() \
            .filter(Q(date__gte=start_date) &
                    Q(date__lte=end_date))
        if period_id is not None:
            attendance_data = attendance_data.filter(period=period_id)
        serializer = AttendanceSerializer(attendance_data, many=True, context={'request': request})
        return Response(data=serializer.data)

    @atomic
    @action(detail=False, methods=['post'])
    def check_in(self, request, employee_pk=None):
        app_config = ApplicationConfig.objects.first()
        employee = get_object_or_404(Employee, pk=employee_pk)
        schedule = employee.get_current_schedule()
        check_in_note = request.data.get('check_in_note', None)

        face_authorized = None
        check_in_outside = None

        # Can check in ?
        if schedule is None:
            return Response(status=status.HTTP_403_FORBIDDEN, data="NO_SCHEDULE")

        serializer = CheckInDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        # Get today attendance
        attendance, today = self.get_today_attendance(employee, schedule)
        period = Period.get_or_create(today)

        # Check if overlapped with an approved time off
        time_off_overlapped = self.check_timeoff_overlapped(employee, today)
        if time_off_overlapped:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="OVERLAPPED_WITH_APPROVED_TIME_OFF")

        # Check if already check in
        if attendance is not None:
            log = attendance.tracking_data.filter(check_out_time=None).first()
            if log is not None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="ALREADY_CHECK_IN")
        else:
            attendance = Attendance(
                owner=employee,
                schedule=schedule,
                date=today,
                period=period,
                status=Attendance.AttendanceLogStatus.Pending
            )
        attendance.save()

        # Face recognition
        face_id_required = getattr(app_config, 'require_face_id', False)
        allow_unrecognised_face = getattr(app_config, 'allow_unrecognised_face', False)
        face_img = request.data.get('face_image', None)
        resized_image = self.scale_image(face_img)

        # No profile picture exception
        if face_id_required and employee.face_model_path is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='Face identity not available')

        if face_img is None and face_id_required:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='face_image required')

        if face_id_required:
            face_authorized = employee.identify_image(resized_image)
            if not face_authorized and not allow_unrecognised_face:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='Face recognition failed')
            if not face_authorized and allow_unrecognised_face and check_in_note is None:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data='Face recognition failed')

        # Check location
        location = employee.get_job_location()
        if location is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="NO_JOB")

        check_in_lat = request.data.get('check_in_lat', None)
        check_in_lng = request.data.get('check_in_lng', None)

        if location.enable_geofencing:
            if check_in_lat is None or check_in_lng is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Geo Info required")

            center = (location.lat, location.lng)
            actual_position = (check_in_lat, check_in_lng)
            dis = distance.distance(center, actual_position).m
            check_in_outside = dis > location.radius
            if check_in_outside and check_in_note is None:
                return Response(status=status.HTTP_400_BAD_REQUEST, data="Check in outside require check_in_note")

        # Create Tracking
        tracking = Tracking(
            attendance=attendance,

            check_in_time=today,

            check_in_lat=check_in_lat,
            check_in_lng=check_in_lng,
            check_in_outside=check_in_outside,

            check_in_note=request.data.get('check_in_note', None),
            location=location,

            check_in_image=face_img,
            check_in_face_authorized=face_authorized,
        )

        tracking.save()
        return Response()

    @staticmethod
    def scale_image(face_img):
        resized_image = None
        if face_img is not None and face_img.file is not None:
            resized_image = Image.open(face_img.file).convert("RGB")

            img_width, img_height = resized_image.size
            max_size = max(img_width, img_height)
            ratio = 1024 / max_size
            resized_image = resized_image.resize((int(img_width * ratio), int(img_height * ratio)), PIL.Image.NEAREST)
        return resized_image

    @staticmethod
    def check_timeoff_overlapped(employee, today):
        time_off_overlapped = TimeOff.objects.filter(
            Q(owner=employee) &
            Q(start_date__lte=today) &
            Q(end_date__gte=today) &
            Q(status=TimeOff.TimeOffStatus.Approved)
        ).exists()
        return time_off_overlapped

    @atomic()
    @action(detail=False, methods=['post'])
    def check_out(self, request, employee_pk):
        app_config = ApplicationConfig.objects.first()
        employee = get_object_or_404(Employee, pk=employee_pk)
        schedule = employee.get_current_schedule()
        check_out_note = request.data.get('check_out_note', None)
        face_authorized = None
        check_out_outside = None

        serializer = CheckOutDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        # Get today attendance
        attendance, today = self.get_today_attendance(employee, schedule)
        if attendance is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data="NOT_CHECK_IN_YET")

        tracking = attendance.tracking_data.filter(check_out_time=None).first()
        if tracking is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Face recognition
        require_face_id = getattr(app_config, 'require_face_id', False)
        allow_unrecognised_face = getattr(app_config, 'allow_unrecognised_face', False)
        face_img = request.data.get('face_image', None)

        if face_img is None and require_face_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data='face_image required')

        # Resize image
        resized_image = self.scale_image(face_img)

        if require_face_id:
            face_authorized = employee.identify_image(resized_image)
            if not face_authorized and not allow_unrecognised_face:
                return Response(status=status.HTTP_400_BAD_REQUEST, data='Face recognition failed')
            if not face_authorized and allow_unrecognised_face and check_out_note is None:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data='Face recognition failed')

        # CHECK OUT OUTSIDE
        check_out_lat = request.data.get('check_out_lat', None)
        check_out_lng = request.data.get('check_out_lng', None)

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
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"error": "Check out outside require check_out_note"})

        # Check Out
        tracking.check_out_time = today
        tracking.check_out_lat = check_out_lat
        tracking.check_out_lng = check_out_lng
        tracking.check_out_note = check_out_note
        tracking.check_out_outside = check_out_outside
        tracking.check_out_image = face_img
        tracking.check_out_face_authorized = face_authorized

        tracking.save()

        tracking.is_overtime = tracking.check_overtime()
        tracking.save()

        # Calculate work hours
        attendance.calculate_work_hours()
        attendance.save()
        return Response()

    @staticmethod
    def get_today_attendance(employee, schedule):
        today = local_now()
        locale_today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        locale_today_end = today.replace(hour=23, minute=59, second=59, microsecond=999999)
        attendance = Attendance.objects \
            .filter(Q(date__gte=locale_today_start) &
                    Q(date__lte=locale_today_end) &
                    Q(owner=employee) &
                    Q(schedule=schedule)) \
            .prefetch_related('tracking_data') \
            .first()
        return attendance, today

    @action(detail=True, methods=['post'])
    def revert(self, request, employee_pk, pk):
        employee = get_object_or_404(Employee, pk=employee_pk)
        attendance = employee.attendance.filter(pk=pk).first()
        if attendance is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if attendance.status == Attendance.AttendanceLogStatus.Pending:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if attendance.status == Attendance.AttendanceLogStatus.Confirmed:
            return Response(status=status.HTTP_403_FORBIDDEN)

        attendance.status = Attendance.AttendanceLogStatus.Pending
        attendance.reviewed_by = None
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

        if attendance.status == Attendance.AttendanceLogStatus.Confirmed or \
                attendance.status == Attendance.AttendanceLogStatus.Rejected:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif attendance.status == Attendance.AttendanceLogStatus.Pending:
            attendance.status = Attendance.AttendanceLogStatus.Approved
            attendance.reviewed_by = author

            attendance.status = Attendance.AttendanceLogStatus.Confirmed
            attendance.confirmed_by = author

        elif attendance.status == Attendance.AttendanceLogStatus.Approved or \
                attendance.status == Attendance.AttendanceLogStatus.Rejected:
            attendance.status = Attendance.AttendanceLogStatus.Confirmed
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

        if attendance.status != Attendance.AttendanceLogStatus.Pending:
            return Response(status=status.HTTP_403_FORBIDDEN)

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

        if attendance.status != Attendance.AttendanceLogStatus.Pending:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = EditOvertimeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        attendance.ot_work_hours = serializer.validated_data.get('ot_work_hours')
        attendance.ot_hours_modified = True
        attendance.ot_hours_modification_note = serializer.validated_data.get('ot_hours_modification_note')

        attendance.save()

        return Response(data=AttendanceSerializer(attendance).data)
