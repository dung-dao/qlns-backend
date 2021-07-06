import os
import uuid

import formulas
import openpyxl
from django.db import models
from django.db.models import Q
from django.utils import timezone
from formulas.errors import FormulaError

from qlns.apps.attendance.models import Attendance, TimeOff, Holiday
from qlns.apps.core.models import Employee, ApplicationConfig
from qlns.apps.payroll.models import SalaryTemplateField
from qlns.apps.payroll.models.PayslipValue import PayslipValue
from qlns.apps.payroll.models.payroll_utils import PIT_VN
from qlns.apps.payroll.models.payslip import Payslip
from qlns.utils.constants import MIN_UTC_DATETIME
from qlns.utils.datetime_utils import to_date_string


def upload_to(instance, filename):
    _, file_extension = os.path.splitext('/' + filename)
    return 'payroll/input_files/' + str(uuid.uuid4()) + file_extension


class InputFileError(Exception):
    pass


class Payroll(models.Model):
    class Meta:
        default_permissions = ('view', 'delete', 'add')
        permissions = (
            ('can_calculate_payroll', 'Can calculate payroll'),
            ('can_export_excel_payroll', 'Can export payroll to excel file'),
            ('can_send_payslip_payroll', 'Can send payslip'),
            ('can_confirm_payroll', 'Can confirm payroll'),
        )

    class Status(models.TextChoices):
        Temporary = 'Temporary'
        Confirmed = 'Confirmed'

    name = models.CharField(max_length=255)
    template = models.ForeignKey(to='SalaryTemplate', on_delete=models.PROTECT, related_name='payrolls')
    period = models.ForeignKey(to='attendance.Period', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.Temporary)
    confirmed_by = models.ForeignKey(to='core.Employee', on_delete=models.SET_NULL, null=True)

    input_file = models.FileField(null=True, upload_to=upload_to)

    def is_inputs_file_required(self):
        return self.template.fields.filter(type='Input').exists()

    @staticmethod
    def get_employee_info(employee):
        return {
            "id": employee.id,
            "first_name": employee.first_name,
            "last_name": employee.last_name,
            "full_name": f'{employee.first_name} {employee.last_name}'.strip(),
            "email": employee.email,
            "gender": employee.gender,
            "birthday": to_date_string(employee.date_of_birth) if employee.date_of_birth is not None else None,
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

            "probation_start_date": to_date_string(
                job.probation_start_date) if job.probation_start_date is not None else None,
            "probation_end_date": to_date_string(
                job.probation_end_date) if job.probation_end_date is not None else None,
            "contract_start_date": to_date_string(
                job.contract_start_date) if job.contract_start_date is not None else None,
            "contract_end_date": to_date_string(
                job.contract_end_date) if job.contract_end_date is not None else None,
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

    def calculate_salary(self):
        if self.status == Payroll.Status.Confirmed:
            return
        # Prepare data
        # Get templates
        template = self.template
        template_fields = template.fields.order_by('index')
        input_fields = template.fields.filter(type='INPUT').order_by('index')

        employees = self.get_payroll_employees()

        self.payslips.all().delete()
        self.save()

        employee_input_list = self.get_all_employee_input(employees, input_fields)

        for index in range(len(employees)):
            employee = employees[index]
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

            inputs = employee_input_list[index]

            calculation_dict = {
                "payroll_start_date": self.period.start_date,
                "payroll_end_date": self.period.end_date,
                **employee_info,
                **job_info,
                **salary_info,
                **work_info,

                **inputs,
            }

            functions = formulas.get_functions()
            functions['PIT_VN'] = PIT_VN

            # Create field value
            for field in template_fields:
                payslip_value = PayslipValue(
                    payslip=payslip,
                    field=field
                )
                # Create system field value for payslip
                if field.type == SalaryTemplateField.SalaryFieldType.SystemField:
                    value = calculation_dict[field.code_name]

                    if field.datatype == SalaryTemplateField.Datatype.Text:
                        payslip_value.str_value = value
                    elif field.datatype == SalaryTemplateField.Datatype.Number or \
                            field.datatype == SalaryTemplateField.Datatype.Currency:
                        payslip_value.num_value = value

                # Create input field value for payslip
                elif field.type == SalaryTemplateField.SalaryFieldType.Input:
                    default_value = 0 \
                        if field.datatype in ('Number', 'Currency',) else ''
                    value = calculation_dict.get(field.code_name, default_value)

                    if field.datatype == SalaryTemplateField.Datatype.Text:
                        payslip_value.str_value = value
                    elif field.datatype == SalaryTemplateField.Datatype.Number or \
                            field.datatype == SalaryTemplateField.Datatype.Currency:
                        payslip_value.num_value = value

                # Create formula field value for payslip
                elif field.type == SalaryTemplateField.SalaryFieldType.Formula:
                    try:
                        formula = formulas.Parser().ast(f'={field.define}')[1].compile()
                    except FormulaError:
                        raise FormulaError('Invalid formula')

                    formula_context = {}
                    inputs = formula.inputs
                    for key in calculation_dict:
                        if key.upper() in inputs:
                            formula_context[key.upper()] = calculation_dict[key]
                    try:
                        ans = formula(**formula_context)
                        # Convert & set value based on defined datatype
                        if field.datatype == SalaryTemplateField.Datatype.Text:
                            value = str(ans)
                            calculation_dict[field.code_name] = value
                            payslip_value.str_value = value
                        elif field.datatype == SalaryTemplateField.Datatype.Number or \
                                field.datatype == SalaryTemplateField.Datatype.Currency:
                            value = float(ans)
                            calculation_dict[field.code_name] = value
                            payslip_value.num_value = value
                    except ValueError:
                        raise ValueError('ValueError in formula')
                    except TypeError:
                        raise TypeError('Invalid formula datatype')
                    except Exception:
                        raise Exception
                payslip_value.save()

    def get_payroll_employees(self):
        # Filter employees and load related data
        employee_query = "SELECT DISTINCT employee.* FROM core_employee employee left join payroll_employeesalary " \
                         "em_salary ON em_salary.owner_id = employee.id left JOIN attendance_employeeschedule " \
                         "em_schedule ON em_schedule.owner_id = employee.id left join job_job job on " \
                         "employee.current_job_id = job.id left join job_termination termination on " \
                         "termination.job_id = job.id WHERE NOT ISNULL(em_salary.id) AND NOT ISNULL(em_schedule.id) " \
                         "AND (ISNULL(termination.`date`) OR termination.`date` > %s)".strip()
        employees = Employee.objects.raw(employee_query, [self.period.start_date.isoformat()])
        return employees

    def get_all_employee_input(self, employees, fields=[]):
        input_lists = []
        try:
            wb = openpyxl.load_workbook(self.input_file, data_only=True)
        except ValueError:
            wb = None
        worksheet = wb.active if wb is not None else None

        # Data read offset
        row_offset = 5
        col_offset = 2

        fields_indxs = range(len(fields))
        for employee_indx in range(len(employees)):
            calculation_dict = {}

            for field_indx in fields_indxs:
                field = fields[field_indx]

                cell_key = f'{chr(col_offset + field_indx + 65)}{employee_indx + row_offset}'

                default_value = 0 \
                    if field.datatype in ('Number', 'Currency',) else ''
                value = worksheet[cell_key].value if worksheet is not None else default_value

                # parse
                try:
                    if field.datatype in ('Number', 'Currency',):
                        value = float(value) if value is not None else 0
                    elif field.datatype in ['Text']:
                        value = str(value) if value is not None else ''
                except ValueError:
                    raise InputFileError

                calculation_dict[field.code_name] = value if value is not None else 0

            input_lists.append(calculation_dict)

        return input_lists
