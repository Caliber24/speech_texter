from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
# Create your models here.



class VTT(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='VTTs',
                             on_delete=models.CASCADE)
    audio = models.FileField(upload_to='audio/', validators=[FileExtensionValidator(allowed_extensions=['mp3', 'wav', 'ogg'])])
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
