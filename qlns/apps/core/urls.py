from django.urls import path, include
from rest_framework_simplejwt import views as jwt_views
from rest_framework.routers import DefaultRouter
from qlns.apps.core.views import EmployeeView, ProfileView, CountryView

router = DefaultRouter()
router.register(r'countries', CountryView, basename='country')
router.register(r'employees', EmployeeView, basename='employee')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', ProfileView.as_view()),
]
