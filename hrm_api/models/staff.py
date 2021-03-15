from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models\
    import AbstractBaseUser, PermissionsMixin, BaseUserManager

from hrm_api.models import Department


class AppAccountManager(BaseUserManager):
    def create_superuser(self, email, username, first_name, last_name, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_superuser', True)

        if other_fields.get('is_staff') is not True or other_fields.get('is_superuser') is not True:
            raise ValueError('is_staff and is_superuser must be set to true')
        return self.create_user(email, username, first_name, last_name, password, **other_fields)

    def create_user(self, email, username, first_name, last_name, password, **other_fields):
        if not email:
            raise ValueError(_("You must provide an email address"))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username,
                          first_name=first_name, last_name=last_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class Staff(AbstractBaseUser, PermissionsMixin):
    def __str__(self):
        return self.username

    objects = AppAccountManager()

    # Config
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(_('email address'), unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    date_joined = models.DateTimeField(default=timezone.now)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    phone = models.CharField(max_length=10, blank=True)
    facebook = models.CharField(max_length=255, blank=True)
    linkedin = models.CharField(max_length=255, blank=True)
    skype = models.CharField(max_length=255, blank=True)

    departments = models.ManyToManyField(
        to=Department,
        through='StaffDepartment',
        through_fields=('staff', 'department')
    )

    def get_role(self):
        if self.is_superuser:
            return "admin".upper()
        g = self.groups.first()
        if g is not None:
            return g.name.upper()
        else:
            return ""


class StaffDepartment(models.Model):
    from_date = models.DateTimeField(null=True, blank=True)
    to_date = models.DateTimeField(null=True, blank=True)
    department = models.ForeignKey(to=Department, on_delete=models.CASCADE)
    staff = models.ForeignKey(to=Staff, on_delete=models.CASCADE)
