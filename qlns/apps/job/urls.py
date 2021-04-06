from django.urls import path, include
from rest_framework_nested import routers

from qlns.apps.job.views import JobTitleView

router = routers.SimpleRouter()

router.register('job_titles', JobTitleView, basename='jobs')

urlpatterns = [
    path('', include(router.urls)),
]