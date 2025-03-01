from django.core.validators import FileExtensionValidator
from django.db import models
from django.conf import settings
from .validators import validate_audio_file


# Create your models here.


class VTT(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='VTTs',
                             on_delete=models.CASCADE)
    audio = models.FileField(validators=[validate_audio_file], help_text='Enter the path to the audio file.')
    transcript = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.audio.name
