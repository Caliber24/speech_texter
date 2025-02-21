import magic
from django.core.exceptions import ValidationError

def validate_audio_file(file_path):
  try:
    mime = magic.Magic(mime=True)
    file_type = mime = mime.from_file(file_path)
    allowed_types = ['audio/mpeg', 'audio/wav', 'audio/ogg']
  
    if file_type not in allowed_types:
      raise ValidationError(f'The file type {file_type} is not allowed. Only MP3, WAV, and OGG files are permitted.')
  except Exception as e:
    raise ValidationError(f'An error occured while validating the file: {e}')
  