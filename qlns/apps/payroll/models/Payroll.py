import formulas
from django.db import models
from django.db.models import Q
from django.db.transaction import atomic

from qlns.apps.core.models import Employee
from qlns.apps.payroll.models import SalaryTemplateField
from qlns.apps.payroll.models.PayslipValue import PayslipValue
from qlns.apps.payroll.models.payslip import Payslip


class Payroll(models.Model):
    name = models.CharField(max_length=255)
    template = models.ForeignKey(to='SalaryTemplate', on_delete=models.PROTECT)
    cycle_start_date = models.DateTimeField()
    cycle_end_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_employee_info(employee):
        return {
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "full_name": f'{employee.first_name} {employee.last_name}'.strip(),
            "email": employee.email,
            "gender": employee.gender,
            "birthday": employee.date_of_birth,
            "phone": employee.phone,
            "nationality": getattr(employee.nationality, 'name', None),
            "personal_tax_id": employee.personal_tax_id,
            "social_insurance": employee.social_insurance,
            "health_insurance": employee.health_insurance,
        }

    @staticmethod
    def get_bank_info(employee):
        return {
            "bank_name": getattr(employee.bank_info, 'bank_name', None),
            "bank_branch": getattr(employee.bank_info, 'branch', None),
            "bank_account_holder": getattr(employee.bank_info, 'account_name', None),
            "bank_account_number": getattr(employee.bank_info, 'account_number', None),
        }

    @staticmethod
    def get_job_info(employee):
        job = employee.get_current_job()

        return {
            "job_title": getattr(job.job_title, 'name', None),
            "department": getattr(job.department, 'name', None),

            "location": getattr(job.location, 'name', None),
            "employment_status": getattr(job.employment_status, 'name', None),

            "probation_start_date": job.probation_start_date,
            "probation_end_date": job.probation_end_date,
            "contract_start_date": job.contract_start_date,
            "contract_end_date": job.contract_end_date,
        }

    @staticmethod
    def get_salary_info(employee):
        if employee.salary_info is None:
            return {
                "salary": None,
                "tax_plan": None,
                "insurance_plan": None,
                "number_of_dependants": None,
            }

        return {
            "salary": employee.salary_info.salary,
            "tax_plan": getattr(employee.salary_info.tax_policy, 'name', None),
            "insurance_plan": getattr(employee.salary_info.insurance_policy, 'name', None),
            "number_of_dependants": employee.Dependents.count(),
        }

    @staticmethod
    def get_work_info(employee, start_date, end_date):
        # attendance = employee.attendance.filter(
        #     Q(date__gte=start_date) &
        #     Q(date__lte=end_date)
        # )

        schedule = employee.get_current_schedule()
        schedule_work_hours = schedule.get_schedule_work_hours() \
            if schedule is not None else 0

        return {
            "schedule_work_point": schedule_work_hours / 8.0,
            "schedule_work_hours": schedule_work_hours,
            "actual_work_point": None,
            "actual_work_hours": None,
            "sum_late": None,
            "deficit": None,
            "days_off": None,
        }

    @atomic
    def calculate_salary(self):
        # Prepare data

        # Get template
        template = self.template
        template_fields = template.fields.order_by('index')

        # Prepare calculation data
        calculation_dict = {}

        employees = Employee.objects \
            .prefetch_related('bank_info') \
            .prefetch_related('job_history') \
            .prefetch_related('salary_info') \
            .filter(
            Q(job_history__isnull=False) &
            Q(salary_info__isnull=False))

        self.payslips.all().delete()
        self.save()

        for employee in employees:
            # Create payslip
            payslip = Payslip(owner=employee, payroll=self)
            payslip.save()

            # Prepare Calculation data
            employee_info = Payroll.get_employee_info(employee)
            job_info = Payroll.get_job_info(employee)
            salary_info = Payroll.get_salary_info(employee)
            work_info = Payroll.get_work_info(employee, None, None)

            calculation_dict = {
                **employee_info,
                **job_info,
                **salary_info,
                **work_info,
            }

            # Create field value
            for field in template_fields:
                payslip_value = PayslipValue(
                    payslip=payslip,
                    field=field
                )

                if field.type == SalaryTemplateField.SalaryFieldType.SystemField:
                    payslip_value.readonly_value = calculation_dict[field.code_name]
                elif field.type == SalaryTemplateField.SalaryFieldType.Formula:
                    formula = formulas.Parser().ast(f'={field.define}')[1].compile()
                    formula_context = {}
                    inputs = formula.inputs
                    for key in calculation_dict:
                        if key.upper() in inputs:
                            formula_context[key.upper()] = calculation_dict[key]
                    try:
                        ans = float(formula(**formula_context))
                        payslip_value.value = ans
                    except ValueError:
                        raise ValueError('Cannot convert to float')
                payslip_value.save()
