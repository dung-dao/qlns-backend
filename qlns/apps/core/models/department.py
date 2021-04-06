from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    manager = models.ForeignKey(
        to='Employee', null=True, on_delete=models.SET_NULL)
    description = models.TextField(blank=True)

    def get_employee_no(self):
        return 7

    def get_manager_full_name(self):
        if self.manager is None:
            return ""
        return f'{self.manager.first_name} {self.manager.last_name}'.strip()

    def get_manager_avatar(self):
        if self.manager is None:
            return None

        return self.manager.avatar