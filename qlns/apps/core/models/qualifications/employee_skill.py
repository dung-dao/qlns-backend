from django.db import  models


class EmployeeSkill(models.Model):
    skill = models.ForeignKey(to='Skill', on_delete=models.CASCADE)
    owner = models.ForeignKey(
        to='Employee', on_delete=models.CASCADE, related_name='skills')
    year_of_experience = models.PositiveSmallIntegerField(null=True)
    note = models.TextField(blank=True)
