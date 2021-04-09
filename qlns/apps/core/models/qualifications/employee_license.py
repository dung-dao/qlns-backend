from django.db import models


class EmployeeLicense(models.Model):
    license_type = models.ForeignKey(to='License', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        to='Employee', on_delete=models.CASCADE, related_name='licenses')
    number = models.CharField(max_length=50)
    issued_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
