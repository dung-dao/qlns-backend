from django.urls import path, include
from rest_framework_nested import routers
from qlns.apps.attendance import views as attendance_views
from qlns.apps.attendance.views.manage_attendance_view import ManageAttendanceView
from qlns.apps.core.urls import router as core_router

router = routers.SimpleRouter()
router.register('schedules', attendance_views.ScheduleView, basename='schedule')
router.register('overtime_types', attendance_views.OvertimeTypeView, basename='overtime_type')

emp_info_router = routers.NestedSimpleRouter(core_router, r'employees', lookup='employee')
emp_info_router.register('schedule', attendance_views.EmployeeScheduleView, basename='employee_schedule')
emp_info_router.register('attendance', attendance_views.EmployeeAttendanceView, basename='employee_attendance')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(emp_info_router.urls)),
    path('attendance', ManageAttendanceView.as_view())
]