from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random
import string

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(None)  # No password initially; set after OTP verification
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        user = self.create_user(phone, **extra_fields)
        if password:
            user.set_password(password)  # Set password for superuser
        user.save(using=self._db)
        return user

class CustomUser(AbstractUser):
    username = None  # Disable username field
    phone = models.CharField(max_length=15, unique=True) 
    name = models.CharField(max_length=100, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.phone

class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='otps')
    code = models.CharField(max_length=6)  # 6-digit OTP
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_otp(self):
        """Generate a random 6-digit OTP."""
        return ''.join(random.choices(string.digits, k=6))

    def save(self, *args, **kwargs):
        """Generate OTP if not set."""
        if not self.code:
            self.code = self.generate_otp()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"OTP {self.code} for {self.user.phone}"