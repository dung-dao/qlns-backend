from django.contrib import admin

from qlns.apps.core import models

# Register your models here.
admin.site.register(models.ApplicationConfig)
admin.site.register(models.Country)
admin.site.register(models.Department)
admin.site.register(models.EducationLevel)
admin.site.register(models.Language)
admin.site.register(models.License)
admin.site.register(models.Skill)

admin.site.register(models.Employee)
