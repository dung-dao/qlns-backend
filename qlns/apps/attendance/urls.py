from django.urls import path, include
from rest_framework_nested import routers

from qlns.apps.attendance import views as attendance_views
from qlns.apps.attendance.views import PeriodView
from qlns.apps.attendance.views.manage_attendance_view import ManageAttendanceView
from qlns.apps.attendance.views.time_off.employee_time_off_view import EmployeeTimeOffView
from qlns.apps.attendance.views.time_off.holiday_view import HolidayView
from qlns.apps.attendance.views.time_off.time_off_type_view import TimeOffTypeView
from qlns.apps.attendance.views.time_off.time_off_view import TimeOffView
from qlns.apps.core.urls import router as core_router

router = routers.SimpleRouter()
router.register('schedules', attendance_views.ScheduleView, basename='schedule')
router.register('holidays', HolidayView, basename='holiday')
router.register('time_off_types', TimeOffTypeView, basename='time_off_type')

router.register('attendance', ManageAttendanceView, basename='attendance')
router.register('attendance/cycle/periods', PeriodView, basename='attendance_period')

emp_info_router = routers.NestedSimpleRouter(core_router, r'employees', lookup='employee')
emp_info_router.register('schedule', attendance_views.EmployeeScheduleView, basename='employee_schedule')
emp_info_router.register('attendance', attendance_views.EmployeeAttendanceView, basename='employee_attendance')
emp_info_router.register('time_off', EmployeeTimeOffView, basename='time_off')
emp_info_router.register('faces', attendance_views.EmployeeFaceView, basename='face')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(emp_info_router.urls)),
    path('time_off/', TimeOffView.as_view()),
    path('attendance_helper/', attendance_views.AttendanceHelper.as_view()),
]
