from django.urls import path, include
from rest_framework_nested import routers
from qlns.apps.job import views as job_views
from qlns.apps.core.urls import router as core_router

router = routers.SimpleRouter()
router.register('job_titles', job_views.JobTitleView, basename='job_title')
router.register('locations', job_views.LocationView, basename='location')
router.register('work_shifts', job_views.WorkShiftView, basename='work_shift')
router.register('employment_statuses', job_views.EmploymentStatusView, basename='employment_status')
router.register('job_events', job_views.JobEventView, basename='job_event')

employee_router = routers.NestedSimpleRouter(core_router, r'employees', lookup='employee')
employee_router.register('jobs', job_views.JobView, basename='job')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(employee_router.urls)),
]