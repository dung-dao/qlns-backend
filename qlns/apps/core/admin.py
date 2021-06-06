from django.contrib import admin
from qlns.apps.core import models

# Register your models here.
admin.site.register(models.Country)
admin.site.register(models.Employee)
admin.site.register(models.EmergencyContact)
admin.site.register(models.ContactInfo)
