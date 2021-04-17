# Admin
from .country import Country
from .department import Department

from .employee import Employee

# PIM
from .contact_info import ContactInfo
from .emergency_contact import EmergencyContact
from .bank_info import BankInfo

# Qualifications
from qlns.apps.core.models.qualifications.license import License
from qlns.apps.core.models.qualifications.language import Language
from qlns.apps.core.models.qualifications.education_level import EducationLevel
from qlns.apps.core.models.qualifications.skill import Skill

# Employee Qualifications
from qlns.apps.core.models.qualifications.employee_license import EmployeeLicense
from qlns.apps.core.models.qualifications.employee_language import EmployeeLanguage
from qlns.apps.core.models.qualifications.employee_education import EmployeeEducation
from qlns.apps.core.models.qualifications.employee_skill import EmployeeSkill
