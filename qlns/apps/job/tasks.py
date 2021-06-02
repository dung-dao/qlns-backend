from qlns.apps.core.models import Employee


def deactivate_employee(employee_id):
    employee = Employee.objects.filter(pk=employee_id).first()
    if employee is None:
        return

    user = employee.user
    user.is_active = False
    user.save()
