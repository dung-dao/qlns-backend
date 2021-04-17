from django.db import models


class BankInfo(models.Model):
    owner = models.OneToOneField(
        to='Employee', on_delete=models.CASCADE, related_name='bank_info')

    bank_name = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255)
    branch = models.CharField(max_length=255)
    account_number = models.CharField(max_length=20)
    swift_bic = models.CharField(max_length=15, blank=True)
    iban = models.CharField(max_length=50, blank=True)