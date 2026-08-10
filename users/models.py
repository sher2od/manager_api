from uuid import RESERVED_FUTURE
from django.db import reset_queries
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        EMPLOYEE = 'employee', 'Employee'

    
    role = models.CharField(
        max_length=50,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        db_index=True
    )

    objects = CustomUserManager()

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_manager(self) -> bool:
        return self.role == self.Role.MANAGER

    @property 
    def is_employee(self) -> bool:
        return self.role == self.Role.EMPLOYEE



































