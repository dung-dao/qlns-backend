from django.contrib import admin
from django.urls import path

# from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.routers import DefaultRouter
from hrm_api.views import RoleViewSet, StaffViewSet, DepartmentViewSet, PermissionViewSet

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='role')
router.register(r'staffs', StaffViewSet, basename='staff')
router.register(r'departments', DepartmentViewSet, basename='department')


# urlpatterns = format_suffix_patterns([
#     path('admin/permissions/', PermissionView.as_view()),
# ])


urlpatterns = router.urls
