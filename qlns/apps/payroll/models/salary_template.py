from django.db import models

from qlns.apps.payroll import models as payroll_models


class SalaryTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def is_modifiable(self):
        has_confirmed_payroll = self.payrolls \
            .filter(status=payroll_models.Payroll.Status.Confirmed) \
            .exists()
        return not has_confirmed_payroll
