from django.urls import path, include
from rest_framework_nested import routers
from qlns.apps.attendance import views as attendance_views
from qlns.apps.core.urls import router as core_router

router = routers.SimpleRouter()
router.register('schedules', attendance_views.ScheduleView, basename='attendance')

emp_info_router = routers.NestedSimpleRouter(core_router, r'employees', lookup='employee')
emp_info_router.register('schedule', attendance_views.EmployeeScheduleView, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(emp_info_router.urls)),
]