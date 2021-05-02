from django.urls import path, include
from rest_framework_nested import routers

from qlns.apps.core.urls import router as core_router
from qlns.apps.payroll import views as _

router = routers.SimpleRouter()
router.register(r'insurance_policies', _.InsurancePolicyView, basename='insurance_policy')
router.register(r'tax_policies', _.TaxPolicyView, basename='tax_policy')
router.register(r'payrolls', _.PayrollView, basename='payroll')

payroll_router = routers.NestedSimpleRouter(router, r'payrolls', lookup='payroll')
payroll_router.register(r'payslips', _.PayrollPayslipsView, basename='payslip')

router.register(r'payroll_config', _.PayrollConfigView, basename='payroll_config')
router.register(r'salary_system_fields', _.SalarySystemFieldView, basename='salary_system_field')
router.register(r'salary_templates', _.SalaryTemplateView, basename='salary_template')

employee_router = routers.NestedSimpleRouter(core_router, r'employees', lookup='employee')
employee_router.register('salary_info', _.EmployeeSalaryView, basename='salary_info')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(employee_router.urls)),
    path('', include(payroll_router.urls)),
]
