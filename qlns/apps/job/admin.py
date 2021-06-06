from django.contrib import admin

from qlns.apps.job import models

# Register your models here.
admin.site.register(models.EmploymentStatus)
admin.site.register(models.JobTitle)
admin.site.register(models.Location)
admin.site.register(models.TerminationReason)
