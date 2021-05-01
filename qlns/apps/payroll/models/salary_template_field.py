from django.db import models


class SalaryTemplateField(models.Model):
    class SalaryFieldType(models.TextChoices):
        SystemField = 'System Field'
        Formula = 'Formula'

    template = models.ForeignKey(to='SalaryTemplate', on_delete=models.CASCADE, related_name='fields')
    index = models.IntegerField()
    type = models.CharField(max_length=50, choices=SalaryFieldType.choices)
    code_name = models.CharField(max_length=255)
    display_name = models.CharField(max_length=255)
    define = models.CharField(max_length=1024, null=True, blank=True)
