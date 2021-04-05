from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    manager = models.ForeignKey(
        to='Employee', null=True, on_delete=models.SET_NULL)
