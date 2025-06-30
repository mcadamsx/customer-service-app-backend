from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        PermissionsMixin, BaseUserManager)
from django.utils import timezone
from datetime import timedelta
import uuid
import secrets
import string


def generate_registration_token():
    prefix = 'ADM'
    charset = string.ascii_uppercase + string.digits
    suffix = ''.join(secrets.choice(charset) for _ in range(9))
    return prefix + suffix


class AdminUserManager(BaseUserManager):
    def create_user(self, company_email, password=None, **extra_fields):
        if not company_email:
            raise ValueError("Email must be set")
        email = self.normalize_email(company_email)
        user = self.model(company_email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, company_email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(company_email, password, **extra_fields)


class AdminUser(AbstractBaseUser, PermissionsMixin):
    company_name = models.CharField(max_length=255)
    company_email = models.EmailField(unique=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = AdminUserManager()

    USERNAME_FIELD = 'company_email'
    REQUIRED_FIELDS = ['company_name']

    def __str__(self):
        return self.company_email


class AdminSignupToken(models.Model):
    email = models.EmailField()
    token = models.CharField(
        max_length=12,
        unique=True,
        default=generate_registration_token,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)

    def __str__(self):
        return f"Token({self.token}) for {self.email}"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=1)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = str(uuid.uuid4()).replace("-", "")
        super().save(*args, **kwargs)


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    location = models.CharField(max_length=100)
    is_online = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customers'
    )

    def __str__(self):
        return self.full_name


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,
                              default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"


class SubAdmin(models.Model):
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True,
                                blank=True)

    def __str__(self):
        return self.full_name
