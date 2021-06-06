from django.contrib import admin

from qlns.apps.attendance import models

# Register your models here.
admin.site.register(models.Holiday)
admin.site.register(models.Schedule)
admin.site.register(models.WorkDay)
admin.site.register(models.TimeOffType)
