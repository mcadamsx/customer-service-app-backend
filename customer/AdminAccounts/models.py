from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
)
from django.utils import timezone
from datetime import timedelta
import uuid
import random
import string
from django.conf import settings


def generate_registration_token():
    prefix = 'ADM'
    suffix = ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=9)
    )
    return prefix + suffix


def generate_customer_token():
    prefix = 'CUS'
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=9))
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
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    is_verified = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        Group,
        related_name='adminuser_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='adminuser_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

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
        return f"Token for {self.user.company_email}"


class AdminEmailVerificationToken(models.Model):
    user = models.OneToOneField('AdminUser', on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"

    @staticmethod
    def generate_token():
        return uuid.uuid4().hex


class CustomerUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class CustomerUser(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_verified = models.BooleanField(default=False)

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # typically your AdminUser model
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invited_customers'
    )

    groups = models.ManyToManyField(
        Group,
        related_name='customeruser_groups',
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customeruser_permissions',
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.'
    )

    objects = CustomerUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email


class CustomerInvitationToken(models.Model):
    admin = models.ForeignKey(
        AdminUser,
        on_delete=models.CASCADE,
        related_name="invitations"
    )
    email = models.EmailField()
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=255)
    token = models.CharField(
        max_length=12,
        unique=True,
        default=generate_customer_token,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)
    invited_by = models.ForeignKey(
        AdminUser,
        on_delete=models.CASCADE,
        related_name='customer_invitation_tokens'
    )

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(days=1)

    def __str__(self):
        return (
            f"Token({self.token}) by {self.admin.company_email} "
            f"for {self.email}"
        )


class CustomerEmailVerificationToken(models.Model):
    user = models.OneToOneField('CustomerUser', on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Token for {self.user.email}"

    @staticmethod
    def generate_token():
        return uuid.uuid4().hex


class PasswordResetToken(models.Model):
    user = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=1)

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


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]

    customer = models.ForeignKey(
        CustomerUser,
        on_delete=models.CASCADE,
        related_name='tickets'
    )
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject}"


class Payment(models.Model):
    customer = models.ForeignKey(
        CustomerUser,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"Payment of {self.amount} {self.currency} by "
            f"{self.customer.full_name}"
        )


class SubAdmin(models.Model):
    admin = models.ForeignKey(AdminUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_subadmins'
    )

    def __str__(self):
        return self.full_name
