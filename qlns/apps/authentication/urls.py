from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from .views import GroupView, PermissionView, AuthenticatedPermissionView, FaceRecognitionView

router = DefaultRouter()
router.register(r'roles', GroupView, basename='role')
router.register(r'permissions', PermissionView, basename='permission')

urlpatterns = [
    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(),
         name='token_refresh'),
    path('', include(router.urls)),
    path('authenticated_permissions/', AuthenticatedPermissionView.as_view()),
    path('detect_faces/', FaceRecognitionView.as_view()),
]
