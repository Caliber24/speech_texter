from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
# Create your models here.



class CustomUserManager(BaseUserManager):
  def create_user(self, imei, password=None, **extra_fields):
    if not imei:
      raise ValueError("IMEI is required.")
    user = self.model(imei=imei, **extra_fields)
    if password:
      user.set_password(password)
    user.save(using=self._db)
    return user
  
  def create_superuser(self, imei, password, **extra_fields):
    extra_fields.setdefault('is_admin', True)
    return self.create_user(imei=imei, password=password, **extra_fields)

class User(AbstractBaseUser):
  imei = models.CharField(unique=True, max_length=15)
  email = models.EmailField(unique=True, null=True, blank=True)
  password = models.CharField(max_length=128, null=True, blank=True)
  is_active = models.BooleanField(default=True)
  is_admin = models.BooleanField(default=False)
  USERNAME_FIELD = 'imei'
  REQUIRED_FIELDS=[]
  objects = CustomUserManager()
  def __str__(self):
    return self.imei
  
  def has_perm(self, perm, obj=None):
    return True
  
  def has_module_perms(self, app_label):
    return True
  @property
  def is_staff(self):
    return self.is_admin
  def set_password(self, raw_password):
    if raw_password :
      self.password = make_password(raw_password)
    else:
      self.password = None
    
    self.save()