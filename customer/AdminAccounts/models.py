from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
import uuid

class AdminUserManager(BaseUserManager):
    def create_user(self, company_email, password=None, **extra_fields):
        if not company_email:
            raise ValueError("Company email is required")
        email = self.normalize_email(company_email)
        user = self.model(company_email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, company_email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(company_email, password, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    registration_token = models.CharField(max_length=12, unique=True, editable=False, blank=True)
    
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(unique=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    street = models.CharField(max_length=255)
    town = models.CharField(max_length=100)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "company_email"
    REQUIRED_FIELDS = ["company_name"]

    objects = AdminUserManager()

    def save(self, *args, **kwargs):
        if not self.registration_token:
            self.registration_token = self.generate_registration_token()
        super().save(*args, **kwargs)

    def generate_registration_token(self):
        return f"ADM{uuid.uuid4().hex[:9].upper()}"

    def __str__(self):
        return self.company_name
