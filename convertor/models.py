from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
from .validators import validate_audio_file


# Create your models here.


class VTT(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='VTTs',
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
