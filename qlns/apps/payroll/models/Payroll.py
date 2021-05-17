from decimal import Decimal

import formulas
from django.db import models
from django.db.models import Q
from django.db.transaction import atomic
from django.utils import timezone

from qlns.apps.attendance.models import Attendance, TimeOff, Holiday
from qlns.apps.core.models import Employee, ApplicationConfig
from qlns.apps.payroll.models import SalaryTemplateField
from qlns.apps.payroll.models.PayslipValue import PayslipValue
from qlns.apps.payroll.models.payroll_utils import PIT_VN
from qlns.apps.payroll.models.payslip import Payslip
from qlns.utils.constants import MIN_UTC_DATETIME


class Payroll(models.Model):
    class Status(models.TextChoices):
        Temporary = 'Temporary'
        Confirmed = 'Confirmed'

    name = models.CharField(max_length=255)
    template = models.ForeignKey(to='SalaryTemplate', on_delete=models.PROTECT, related_name='payrolls')
    period = models.ForeignKey(to='attendance.Period', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.Temporary)

    @staticmethod
    def get_employee_info(employee):
        return {
            "id": employee.id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "full_name": f'{employee.first_name} {employee.last_name}'.strip(),
            "email": employee.email,
            "gender": employee.gender,
            "birthday": employee.date_of_birth,
            "phone": employee.phone,
            "nationality": employee.nationality.name if employee.nationality is not None else None,
            "personal_tax_id": employee.personal_tax_id,
            "social_insurance": employee.social_insurance,
            "health_insurance": employee.health_insurance,
        }

    @staticmethod
    def get_bank_info(employee):
        res_dict = {
            'bank_name': None,
            'bank_branch': None,
            'bank_account_holder': None,
            'bank_account_number': None
        }

        if employee.bank_info is not None:
            res_dict['bank_name'] = employee.bank_info.bank_name
            res_dict['bank_branch'] = employee.bank_info.branch
            res_dict['bank_account_holder'] = employee.bank_info.account_name
            res_dict['bank_account_number'] = employee.bank_info.account_number

        return res_dict

    @staticmethod
    def get_job_info(employee):
        job = employee.get_current_job()
        if job is None:
            return {
                "job_title": None,
                "department": None,

                "location": None,
                "employment_status": None,

                "probation_start_date": None,
                "probation_end_date": None,
                "contract_start_date": None,
                "contract_end_date": None,
            }

        return {
            "job_title": job.job_title.name if job is not None else None,
            "department": job.department.name if job.department is not None else None,

            "location": job.location.name if job.location is not None else None,
            "employment_status": job.employment_status.name if job.employment_status is not None else None,

            "probation_start_date": job.probation_start_date,
            "probation_end_date": job.probation_end_date,
            "contract_start_date": job.contract_start_date,
            "contract_end_date": job.contract_end_date,
        }

    @staticmethod
    def get_salary_info(employee):
        if employee.salary_info is None:
            return {
                "salary": 0,
                "basic_salary": 0,
                "tax_plan_code": None,
                "tax_plan_name": None,
                "insurance_plan_code": None,
                "insurance_plan_name": None,
                "number_of_dependants": 0,
            }

        salary = employee.salary_info.salary
        basic_salary = employee.salary_info.basic_salary
        tax_plan_code = employee.salary_info.tax_policy.code
        tax_plan_name = employee.salary_info.tax_policy.name

        insurance_plan_name = employee.salary_info.insurance_policy.name
        insurance_plan_code = employee.salary_info.insurance_policy.code

        number_of_dependants = employee.Dependents.count()
        return {
            "salary": salary,
            "basic_salary": basic_salary,

            "tax_plan_code": tax_plan_code,
            "tax_plan_name": tax_plan_name,

            "insurance_plan_code": insurance_plan_code,
            "insurance_plan_name": insurance_plan_name,
            "number_of_dependants": number_of_dependants,
        }

    @staticmethod
    def get_work_info(employee, cycle_start_date, cycle_end_date):
        schedule = employee.get_current_schedule()
        _schedule_work_point = schedule.get_work_hours(cycle_start_date, cycle_end_date) / 8.0

        # ACTUAL WORK POINT
        attendance_data = employee.attendance.filter(
            Q(date__gte=cycle_start_date) &
            Q(date__lte=cycle_end_date) &
            Q(status=Attendance.AttendanceLogStatus.Confirmed)
        )

        def map_attendance_to_work_point(attendance):
            return attendance.actual_work_hours / 8.0

        _normal_work_point = sum(map(map_attendance_to_work_point, attendance_data))

        # OT WORK POINT
        app_config = ApplicationConfig.objects.first()
        ot_point_rate = app_config.ot_point_rate

        def map_attendance_to_ot_work_point(attendance):
            return attendance.ot_work_hours / 8.0 * ot_point_rate

        _overtime_work_point = sum(map(map_attendance_to_ot_work_point, attendance_data))

        # PAID TIME OFF
        pto_data = employee.TimeOff.filter(
            Q(start_date__gte=cycle_start_date) &
            Q(start_date__lte=cycle_end_date) &
            Q(status=TimeOff.TimeOffStatus.Approved) &
            Q(time_off_type__is_paid=True)
        )

        def map_pto_to_work_point(pto):
            return pto.trim_work_hours(cycle_start_date, cycle_end_date) / 8.0

        _paid_time_off_point = sum(map(map_pto_to_work_point, pto_data))

        # HOLIDAY POINT
        holiday_data = Holiday.objects.filter(
            Q(start_date__gte=cycle_start_date) &
            Q(start_date__lte=cycle_end_date) &
            Q(schedule=schedule)
        )

        def map_holiday_to_holiday_point(holiday):
            return holiday.trim_work_hours(cycle_start_date, cycle_end_date) / 24

        _holiday_point = sum(map(map_holiday_to_holiday_point, holiday_data))

        # TODO: COUNT LATE
        def count_late_attendance(attendance):
            attendance_date = timezone.localtime(attendance.date)

            trackers = attendance.tracking_data.all()
            workday = schedule.shift_workday(attendance_date, attendance_date.weekday())

            def check_late_tracker(tracker):
                if workday is None:
                    return False

                morning_from = workday.get('morning_from', MIN_UTC_DATETIME)
                morning_to = workday.get('morning_to', MIN_UTC_DATETIME)

                afternoon_from = workday.get('afternoon_from', MIN_UTC_DATETIME)
                afternoon_to = workday.get('afternoon_to', MIN_UTC_DATETIME)

                if morning_from < tracker.check_in_time < morning_to or \
                        afternoon_from < tracker.check_in_time < afternoon_to:
                    return True
                else:
                    return False

            return len(list(filter(check_late_tracker, trackers)))

        count_late_attendance = sum(map(count_late_attendance, attendance_data))

        return {
            "schedule_work_point": _schedule_work_point,
            "actual_work_point": _normal_work_point + _overtime_work_point + _paid_time_off_point + _holiday_point,
            "normal_work_point": _normal_work_point,
            "overtime_work_point": _overtime_work_point,
            "paid_time_off_point": _paid_time_off_point,
            "holiday_point": _holiday_point,
            "sum_late": count_late_attendance
        }

    @atomic
    def calculate_salary(self):
        if self.status == Payroll.Status.Confirmed:
            return
        # Prepare data

        # Get templates
        template = self.template
        template_fields = template.fields.order_by('index')

        # Prepare calculation data

        employees = Employee.objects \
            .prefetch_related('bank_info') \
            .prefetch_related('job_history') \
            .prefetch_related('salary_info') \
            .filter(Q(job_history__isnull=False) &
                    Q(salary_info__isnull=False) &
                    Q(employee_schedule__isnull=False)) \
            .filter(current_job__isnull=False) \
            .filter(current_job__isnull=False) \
            .distinct()

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
            work_info = Payroll.get_work_info(employee,
                                              self.period.start_date,
                                              self.period.end_date)

            calculation_dict = {
                "payroll_start_date": self.period.start_date,
                "payroll_end_date": self.period.end_date,
                **employee_info,
                **job_info,
                **salary_info,
                **work_info,
            }

            functions = formulas.get_functions()
            functions['PIT_VN'] = PIT_VN

            # Create field value
            for field in template_fields:
                payslip_value = PayslipValue(
                    payslip=payslip,
                    field=field
                )

                if field.type == SalaryTemplateField.SalaryFieldType.SystemField:
                    value = calculation_dict[field.code_name]
                    t = type(value)
                    if type(value) == str:
                        payslip_value.str_value = value
                    elif type(value) == int or type(value) == float or type(value) == Decimal:
                        payslip_value.num_value = value
                    else:
                        raise Exception('Unresolved datatype')

                elif field.type == SalaryTemplateField.SalaryFieldType.Formula:
                    formula = formulas.Parser().ast(f'={field.define}')[1].compile()
                    formula_context = {}
                    inputs = formula.inputs
                    for key in calculation_dict:
                        if key.upper() in inputs:
                            formula_context[key.upper()] = calculation_dict[key]
                    try:
                        ans = float(formula(**formula_context))
                        calculation_dict[field.code_name] = ans
                        payslip_value.num_value = ans
                    except ValueError:
                        raise ValueError('Cannot convert to float')
                payslip_value.save()
