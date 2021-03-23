from django.conf.urls import url
from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from .views import GroupView, PermissionView, EmployeeView, ProfileView, AuthenticatedPermissionView, CountryView

router = DefaultRouter()
router.register(r'roles', GroupView, basename='role')
router.register(r'permissions', PermissionView, basename='permission')
router.register(r'countries', CountryView, basename='country')
router.register(r'employees', EmployeeView, basename='employee')

urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('', include(router.urls)),
    path('profile/', ProfileView.as_view()),
    path('authenticated_permissions/', AuthenticatedPermissionView.as_view()),

]
