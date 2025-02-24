import mimetypes
from django.core.exceptions import ValidationError


def validate_audio_file(file):
    allowed_types = ['audio/mpeg', 'audio/wav', 'audio/ogg']
    mime_type, _ = mimetypes.guess_type(file.name)

    if mime_type not in allowed_types:
        raise ValidationError(
            f'The file type {mime_type} is not allowed. Only {", ".join(allowed_types)} files are permitted.'
        )
  