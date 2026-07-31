from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager



class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        MANAGER = 'manager', 'Manager'
        EMPLOYEE = 'employee', 'Employee'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE
    )


    objects = CustomUserManager()

    