from django.urls import path, include
from rest_framework_nested import routers
from qlns.apps.core import views as core_views

router = routers.SimpleRouter()
router.register(r'countries', core_views.CountryView, basename='country')
router.register(r'employees', core_views.EmployeeView, basename='employee')

pim_router = routers.NestedSimpleRouter(
    router, r'employees', lookup='employee')

pim_router.register(
    'contact_info', core_views.ContactInfoView, basename='contact_info')
pim_router.register(
    'emergency_contact', core_views.EmergencyContactView, basename='emergency_contact')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(pim_router.urls))
]
