from django.contrib import admin

from qlns.apps.payroll import models

# Register your models here.
admin.site.register(models.InsurancePolicy)
admin.site.register(models.TaxPolicy)
admin.site.register(models.PayrollConfig)
admin.site.register(models.SalarySystemField)
