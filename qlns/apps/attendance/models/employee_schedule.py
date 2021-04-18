from django.db import models


class EmployeeSchedule(models.Model):
    owner = models.ForeignKey(to='core.Employee', on_delete=models.CASCADE, related_name='schedule')
    schedule = models.ForeignKey(to='Schedule', on_delete=models.CASCADE, related_name='employee_schedule')
