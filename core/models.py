from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
# Create your models here.


def create_superuser(self, email, password, **extra_fields):
  extra_fields.setdefault('is_staff', True)
  extra_fields.setdefault('is_superuser', True)
  return self.create_user(email, password, **extra_fields)

class CustomUserManager(BaseUserManager):
  def create_user(self, email, password=None, **extra_fields):
    if not email:
      raise ValueError('You must provide an email address')
    email = self.normalize_email(email)
    user = self.model(email=email, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user
  
  def create_superuser(self, email, password, **extra_fields):
    extra_fields.setdefault('is_staff', True)
    extra_fields.setdefault('is_superuser', True)
    return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
  first_name = models.CharField(max_length=255, null=True, blank=True)
  last_name = models.CharField(max_length=255, null=True, blank=True)
  username = models.CharField(max_length=255, null=True, blank=True)
  email = models.EmailField(unique=True)
  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS=[]
  last_login = models.DateTimeField(null=True, blank=True, auto_now_add=True)
  objects = CustomUserManager()