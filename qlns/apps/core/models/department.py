from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    manager = models.ForeignKey(
        to='Employee', null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)

    def get_employee_no(self):
        return 7
