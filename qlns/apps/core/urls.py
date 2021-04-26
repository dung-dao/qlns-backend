from django.urls import path, include
from rest_framework_nested import routers

from qlns.apps.core import views as core_views
from qlns.apps.core.views import qualifications

router = routers.SimpleRouter()

router.register(r'countries', core_views.CountryView, basename='country')
router.register(r'departments', core_views.DepartmentView, basename='department')

router.register(r'licenses', qualifications.LicenseView, basename='license')
router.register(r'languages', qualifications.LanguageView, basename='license')
router.register(r'education_levels', qualifications.EducationLevelView, basename='education_level')
router.register(r'skills', qualifications.SkillView, basename='skill')


router.register(r'employees', core_views.EmployeeView, basename='employee')

pim_router = routers.NestedSimpleRouter(router, r'employees', lookup='employee')
profile_urlpatterns = [
    path('auth/current_user/', core_views.ProfileView.as_view()),
    path('auth/current_user/password/', core_views.ChangePasswordView.as_view()),
    path('auth/current_user/avatar/', core_views.ChangeAvatarView.as_view()),
]

pim_router.register('contact_info', core_views.ContactInfoView, basename='contact_info')
pim_router.register('emergency_contact', core_views.EmergencyContactView, basename='emergency_contact')
pim_router.register('bank_info', core_views.BankInfoView, basename='bank_info')

pim_router.register('licenses', qualifications.EmployeeLicenseView, basename='employee_license')
pim_router.register('languages', qualifications.EmployeeLanguageView, basename='employee_language')
pim_router.register('education', qualifications.EmployeeEducationView, basename='education')
pim_router.register('skills', qualifications.EmployeeSkillView, basename='skill')

pim_router.register('dependents', core_views.DependentView, basename='dependent')
urlpatterns = [
    path('', include(router.urls)),
    path('', include(pim_router.urls)),
    *profile_urlpatterns,
]

