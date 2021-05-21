from django.db import models

from qlns.apps.core import models as core_models


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    manager = models.ForeignKey(
        to='Employee', null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)

    def get_employee_no(self):
        query = "SELECT DISTINCT employee.id FROM core_employee employee LEFT JOIN job_job job ON " \
                "employee.current_job_id = job.id LEFT JOIN job_termination termination ON termination.job_id = " \
                "job.id WHERE job.department_id = %s AND (ISNULL(termination.`date`) OR termination.`date` >= NOW()) "
        return len(list(core_models.Employee.objects.raw(query, [self.pk])))

    def get_manager_full_name(self):
        if self.manager is None:
            return ""
        return f'{self.manager.first_name} {self.manager.last_name}'.strip()

    def get_manager_avatar(self):
        if self.manager is None:
            return None

        return self.manager.avatar
