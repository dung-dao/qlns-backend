from django.urls import path, include
from rest_framework_nested import routers

from qlns.apps.core import views as core_views

router = routers.SimpleRouter()

router.register(r'countries', core_views.CountryView, basename='country')
router.register(r'departments', core_views.DepartmentView, basename='department')
router.register(r'employees', core_views.EmployeeView, basename='employee')

pim_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
profile_urlpatterns = [
    path('auth/current_user/', core_views.ProfileView.as_view()),
    path('auth/current_user/password', core_views.ChangePasswordView.as_view()),
    path('auth/current_user/avatar', core_views.ChangeAvatarView.as_view()),
]

pim_router.register('contact_info', core_views.ContactInfoView, basename='contact_info')
pim_router.register('emergency_contact', core_views.EmergencyContactView, basename='emergency_contact')
pim_router.register('bank_info', core_views.BankInfoView, basename='bank_info')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(pim_router.urls)),
    *profile_urlpatterns,
]

