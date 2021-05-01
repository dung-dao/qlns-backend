from django.urls import path, include
from rest_framework_nested import routers

from qlns.apps.core.urls import router as core_router
from qlns.apps.payroll import views as _

router = routers.SimpleRouter()
router.register(r'insurance_policies', _.InsurancePolicyView, basename='insurance_policy')
router.register(r'tax_policies', _.TaxPolicyView, basename='tax_policy')

employee_router = routers.NestedSimpleRouter(core_router, r'employees', lookup='employee')
employee_router.register('salary_info', _.EmployeeSalaryView, basename='salary_info')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(employee_router.urls)),
]
