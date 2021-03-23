from django.contrib import admin
from qlns.apps.authentication import models

# Register your models here.
admin.site.register(models.Employee)
admin.site.register(models.Country)
