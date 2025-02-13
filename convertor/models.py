from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from django.db import models
from django .contrib.auth.models import User
# Create your models here.



class VTT(models.Model):
    user = models.ForeignKey(User, related_name='VTTs',
                             on_delete=models.CASCADE)
    audio = models.FileField(upload_to='audio/', validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg'])])
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
