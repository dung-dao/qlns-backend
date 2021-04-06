from django.urls import path, include
from rest_framework_nested import routers

from qlns.apps.job import views as job_views

router = routers.SimpleRouter()

router.register('job_titles', job_views.JobTitleView, basename='job')
router.register('locations', job_views.LocationView, basename='location')
router.register('work_shifts', job_views.WorkShiftView, basename='work_shift')

urlpatterns = [
    path('', include(router.urls)),
]